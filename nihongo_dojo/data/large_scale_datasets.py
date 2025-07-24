"""
Large-scale dataset generation and management for Nihongo DoJo
Supports 100k+ dataset generation for GRPO training
"""

import json
import gzip
import pickle
import hashlib
from typing import List, Dict, Optional, Union, Tuple, Iterator
from pathlib import Path
from dataclasses import dataclass, asdict
import numpy as np
from tqdm import tqdm
import multiprocessing as mp
from functools import partial
import random
from datetime import datetime

from ..core import TaskType, TaskDifficulty, NihongoDoJo
from .datasets import NihongoGRPODataset, create_mixed_dataset


@dataclass
class DatasetMetadata:
    """データセットのメタデータ"""
    name: str
    version: str
    created_at: str
    num_tasks: int
    num_groups: int
    task_types: List[str]
    difficulty_distribution: Dict[str, float]
    file_format: str
    compression: str
    checksum: str
    description: str


class LargeScaleDatasetGenerator:
    """大規模データセット生成クラス"""
    
    def __init__(self, num_workers: int = None):
        """
        Initialize large-scale dataset generator
        
        Args:
            num_workers: 並列処理のワーカー数（Noneの場合はCPU数-1）
        """
        self.num_workers = num_workers or max(1, mp.cpu_count() - 1)
        self.dojo = NihongoDoJo()
        
    def generate_large_dataset(
        self,
        total_tasks: int = 100000,
        task_type_distribution: Optional[Dict[str, float]] = None,
        difficulty_distribution: Optional[Dict[TaskDifficulty, float]] = None,
        group_size: int = 4,
        batch_size: int = 1000,
        seed: int = 42
    ) -> Tuple[List[Dict], DatasetMetadata]:
        """
        大規模データセットを生成
        
        Args:
            total_tasks: 総タスク数（デフォルト: 100,000）
            task_type_distribution: タスクタイプの分布
            difficulty_distribution: 難易度の分布
            group_size: GRPOグループサイズ
            batch_size: バッチ処理サイズ
            seed: ランダムシード
            
        Returns:
            (データセット, メタデータ)のタプル
        """
        random.seed(seed)
        np.random.seed(seed)
        
        # デフォルト分布
        if task_type_distribution is None:
            task_type_distribution = {
                'basic': 0.6,      # 基本タスク
                'advanced': 0.3,   # 拡張タスク
                'cultural': 0.1    # 文化タスク
            }
        
        if difficulty_distribution is None:
            difficulty_distribution = {
                TaskDifficulty.BEGINNER: 0.25,
                TaskDifficulty.INTERMEDIATE: 0.35,
                TaskDifficulty.ADVANCED: 0.25,
                TaskDifficulty.NATIVE: 0.15
            }
        
        print(f"🚀 大規模データセット生成開始: {total_tasks:,}タスク")
        print(f"   ワーカー数: {self.num_workers}")
        print(f"   バッチサイズ: {batch_size}")
        
        # バッチ分割
        num_batches = (total_tasks + batch_size - 1) // batch_size
        batches = []
        for i in range(num_batches):
            start_idx = i * batch_size
            end_idx = min((i + 1) * batch_size, total_tasks)
            batch_tasks = end_idx - start_idx
            batches.append({
                'batch_id': i,
                'num_tasks': batch_tasks,
                'task_type_dist': task_type_distribution,
                'difficulty_dist': difficulty_distribution,
                'seed': seed + i
            })
        
        # 並列処理でバッチ生成
        all_tasks = []
        with mp.Pool(processes=self.num_workers) as pool:
            results = list(tqdm(
                pool.imap(self._generate_batch, batches),
                total=len(batches),
                desc="バッチ生成"
            ))
            
            for batch_tasks in results:
                all_tasks.extend(batch_tasks)
        
        # None値を除外
        all_tasks = [task for task in all_tasks if task is not None]
        
        print(f"✅ タスク生成完了: {len(all_tasks):,}タスク")
        
        # GRPOグループ作成
        print("📦 GRPOグループ作成中...")
        groups = self._create_grpo_groups(all_tasks, group_size)
        
        # 学習フォーマットに変換
        print("🔄 学習フォーマットに変換中...")
        training_data = self._convert_to_training_format(groups)
        
        # メタデータ作成
        metadata = self._create_metadata(
            name=f"nihongo_dojo_large_{total_tasks}",
            num_tasks=len(all_tasks),
            num_groups=len(groups),
            task_type_distribution=task_type_distribution,
            difficulty_distribution=difficulty_distribution,
            training_data=training_data
        )
        
        print(f"✅ データセット生成完了!")
        print(f"   タスク数: {metadata.num_tasks:,}")
        print(f"   グループ数: {metadata.num_groups:,}")
        
        return training_data, metadata
    
    def _generate_batch(self, batch_config: Dict) -> List[Dict]:
        """バッチ単位でタスクを生成（並列処理用）"""
        random.seed(batch_config['seed'])
        dojo = NihongoDoJo()  # 各プロセスでインスタンス生成
        
        tasks = []
        task_type_dist = batch_config['task_type_dist']
        difficulty_dist = batch_config['difficulty_dist']
        
        # タスクタイプのカテゴリ分け
        task_categories = {
            'basic': [
                TaskType.KANJI_READING,
                TaskType.KANJI_WRITING,
                TaskType.PARTICLE_FILL,
                TaskType.KEIGO_CONVERSION,
                TaskType.WORD_ORDER,
                TaskType.COUNTER_WORD,
            ],
            'advanced': [
                TaskType.ADVANCED_GRAMMAR,
                TaskType.ONOMATOPOEIA,
                TaskType.CONVERSATION,
                TaskType.PROVERB_IDIOM,
                TaskType.BUSINESS_JAPANESE,
                TaskType.CLASSICAL_JAPANESE,
                TaskType.SPECIALIZED_VOCABULARY
            ],
            'cultural': [
                TaskType.SEASONAL_EXPRESSION,
                TaskType.SOCIAL_CONTEXT,
                TaskType.REGIONAL_DIALECT,
                TaskType.AGE_GENDER_LANGUAGE,
                TaskType.EMOTIONAL_EXPRESSION
            ]
        }
        
        for _ in range(batch_config['num_tasks']):
            # カテゴリ選択
            category = np.random.choice(
                list(task_type_dist.keys()),
                p=list(task_type_dist.values())
            )
            
            # タスクタイプ選択
            task_type = random.choice(task_categories[category])
            
            # 難易度選択
            difficulty = np.random.choice(
                list(difficulty_dist.keys()),
                p=list(difficulty_dist.values())
            )
            
            # タスク生成
            try:
                task = dojo.generate_task(task_type=task_type, difficulty=difficulty)
                tasks.append(task)
            except Exception as e:
                print(f"Warning: Failed to generate task {task_type}: {e}")
                continue
        
        return tasks
    
    def _create_grpo_groups(self, tasks: List[Dict], group_size: int) -> List[List[Dict]]:
        """GRPOグループを作成"""
        # None値を除外してシャッフル
        valid_tasks = [task for task in tasks if task is not None]
        shuffled_tasks = valid_tasks.copy()
        random.shuffle(shuffled_tasks)
        
        # グループ作成
        groups = []
        for i in range(0, len(shuffled_tasks), group_size):
            group = shuffled_tasks[i:i + group_size]
            if len(group) == group_size:  # 完全なグループのみ
                groups.append(group)
        
        return groups
    
    def _convert_to_training_format(self, groups: List[List[Dict]]) -> List[Dict]:
        """学習フォーマットに変換"""
        training_data = []
        
        for group_id, group in enumerate(groups):
            for task_idx, task in enumerate(group):
                # JapaneseTaskオブジェクトを辞書に変換
                if hasattr(task, '__dataclass_fields__'):
                    # dataclassの場合
                    difficulty_value = task.difficulty.value if hasattr(task.difficulty, 'value') else task.difficulty
                    task_type_value = task.type.value if hasattr(task.type, 'value') else task.type
                    instruction = task.instruction
                    question = task.question
                    answer = task.answer
                    explanation = task.explanation or ''
                else:
                    # 既に辞書の場合
                    difficulty_value = task['difficulty']
                    task_type_value = task['type']
                    instruction = task.get('instruction', '次の問題に答えてください。')
                    question = task.get('question', task.get('problem', ''))
                    answer = task.get('answer', task.get('solution', ''))
                    explanation = task.get('explanation', task.get('reasoning', ''))
                
                # 難易度に応じたフォーマット（すべて統一）
                reasoning_start = "<think>"
                reasoning_end = "</think>"
                
                # 応答フォーマット
                formatted_output = f"{reasoning_start}\n{explanation}\n{reasoning_end}\n<answer>{answer}</answer>"
                
                example = {
                    "instruction": instruction,
                    "input": question,
                    "output": formatted_output,
                    "group_id": group_id,
                    "task_idx": task_idx,
                    "task_type": task_type_value,
                    "difficulty": difficulty_value,
                    "metadata": {
                        "question": question,
                        "answer": answer,
                        "reasoning": explanation,
                        "created_at": datetime.now().isoformat()
                    }
                }
                
                training_data.append(example)
        
        return training_data
    
    def _create_metadata(
        self,
        name: str,
        num_tasks: int,
        num_groups: int,
        task_type_distribution: Dict,
        difficulty_distribution: Dict,
        training_data: List[Dict]
    ) -> DatasetMetadata:
        """メタデータを作成"""
        # チェックサム計算
        data_str = json.dumps(training_data, sort_keys=True)
        checksum = hashlib.sha256(data_str.encode()).hexdigest()
        
        # タスクタイプ統計
        task_types = {}
        for item in training_data:
            task_type = item['task_type']
            task_types[task_type] = task_types.get(task_type, 0) + 1
        
        return DatasetMetadata(
            name=name,
            version="1.0.0",
            created_at=datetime.now().isoformat(),
            num_tasks=num_tasks,
            num_groups=num_groups,
            task_types=list(task_types.keys()),
            difficulty_distribution={k.value: v for k, v in difficulty_distribution.items()},
            file_format="json",
            compression="gzip",
            checksum=checksum,
            description=f"Nihongo DoJo large-scale dataset with {num_tasks:,} tasks for GRPO training"
        )


class DatasetSerializer:
    """データセットのシリアライズ・デシリアライズ"""
    
    @staticmethod
    def save_dataset(
        data: List[Dict],
        metadata: DatasetMetadata,
        output_dir: str,
        format: str = "jsonl",
        compress: bool = True,
        chunk_size: int = 10000
    ):
        """
        データセットを保存
        
        Args:
            data: データセット
            metadata: メタデータ
            output_dir: 出力ディレクトリ
            format: 保存形式（json, jsonl, pickle）
            compress: 圧縮するか
            chunk_size: チャンクサイズ（大規模データセット用）
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # メタデータ保存
        metadata_path = output_path / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            # metadataが既に辞書の場合はそのまま使用、dataclassの場合はasdict()を使用
            if hasattr(metadata, '__dataclass_fields__'):
                json.dump(asdict(metadata), f, ensure_ascii=False, indent=2)
            else:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"💾 データセット保存中: {output_dir}")
        
        if len(data) > chunk_size:
            # チャンク分割保存
            num_chunks = (len(data) + chunk_size - 1) // chunk_size
            for i in tqdm(range(num_chunks), desc="チャンク保存"):
                start_idx = i * chunk_size
                end_idx = min((i + 1) * chunk_size, len(data))
                chunk_data = data[start_idx:end_idx]
                
                if format == "jsonl":
                    filename = f"data_chunk_{i:04d}.jsonl"
                    if compress:
                        filename += ".gz"
                        with gzip.open(output_path / filename, 'wt', encoding='utf-8') as f:
                            for item in chunk_data:
                                f.write(json.dumps(item, ensure_ascii=False) + '\n')
                    else:
                        with open(output_path / filename, 'w', encoding='utf-8') as f:
                            for item in chunk_data:
                                f.write(json.dumps(item, ensure_ascii=False) + '\n')
                
                elif format == "pickle":
                    filename = f"data_chunk_{i:04d}.pkl"
                    if compress:
                        filename += ".gz"
                        with gzip.open(output_path / filename, 'wb') as f:
                            pickle.dump(chunk_data, f)
                    else:
                        with open(output_path / filename, 'wb') as f:
                            pickle.dump(chunk_data, f)
        else:
            # 単一ファイル保存
            if format == "json":
                filename = "data.json"
                if compress:
                    filename += ".gz"
                    with gzip.open(output_path / filename, 'wt', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                else:
                    with open(output_path / filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
            
            elif format == "jsonl":
                # データが辞書の場合（split毎のデータ）と配列の場合を処理
                if isinstance(data, dict):
                    # split毎にファイルを作成
                    for split, split_data in data.items():
                        filename = f"{split}.jsonl"
                        if compress:
                            filename += ".gz"
                            with gzip.open(output_path / filename, 'wt', encoding='utf-8') as f:
                                for item in split_data:
                                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
                        else:
                            with open(output_path / filename, 'w', encoding='utf-8') as f:
                                for item in split_data:
                                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
                else:
                    # データが配列の場合
                    filename = "data.jsonl"
                    if compress:
                        filename += ".gz"
                        with gzip.open(output_path / filename, 'wt', encoding='utf-8') as f:
                            for item in data:
                                f.write(json.dumps(item, ensure_ascii=False) + '\n')
                    else:
                        with open(output_path / filename, 'w', encoding='utf-8') as f:
                            for item in data:
                                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"✅ データセット保存完了: {output_dir}")
    
    @staticmethod
    def load_dataset(dataset_dir: str) -> Tuple[List[Dict], DatasetMetadata]:
        """
        データセットを読み込む
        
        Args:
            dataset_dir: データセットディレクトリ
            
        Returns:
            (データ, メタデータ)のタプル
        """
        dataset_path = Path(dataset_dir)
        
        # メタデータ読み込み
        metadata_path = dataset_path / "metadata.json"
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata_dict = json.load(f)
            metadata = DatasetMetadata(**metadata_dict)
        
        print(f"📂 データセット読み込み中: {dataset_dir}")
        
        # データ読み込み
        data = []
        
        # チャンクファイルを探す
        chunk_files = sorted(dataset_path.glob("data_chunk_*.jsonl*")) + \
                     sorted(dataset_path.glob("data_chunk_*.pkl*"))
        
        if chunk_files:
            # チャンク読み込み
            for chunk_file in tqdm(chunk_files, desc="チャンク読み込み"):
                if chunk_file.suffix == '.gz':
                    if '.jsonl' in chunk_file.name:
                        with gzip.open(chunk_file, 'rt', encoding='utf-8') as f:
                            for line in f:
                                data.append(json.loads(line))
                    elif '.pkl' in chunk_file.name:
                        with gzip.open(chunk_file, 'rb') as f:
                            chunk_data = pickle.load(f)
                            data.extend(chunk_data)
                else:
                    if chunk_file.suffix == '.jsonl':
                        with open(chunk_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                data.append(json.loads(line))
                    elif chunk_file.suffix == '.pkl':
                        with open(chunk_file, 'rb') as f:
                            chunk_data = pickle.load(f)
                            data.extend(chunk_data)
        else:
            # 単一ファイル読み込み
            data_files = list(dataset_path.glob("data.*"))
            if data_files:
                data_file = data_files[0]
                if data_file.suffix == '.gz':
                    with gzip.open(data_file, 'rt', encoding='utf-8') as f:
                        if '.json' in data_file.name:
                            data = json.load(f)
                        elif '.jsonl' in data_file.name:
                            data = [json.loads(line) for line in f]
                else:
                    with open(data_file, 'r', encoding='utf-8') as f:
                        if data_file.suffix == '.json':
                            data = json.load(f)
                        elif data_file.suffix == '.jsonl':
                            data = [json.loads(line) for line in f]
        
        print(f"✅ データセット読み込み完了: {len(data):,}件")
        
        return data, metadata


class DatasetLoader:
    """効率的なデータセットローダー"""
    
    def __init__(self, dataset_dir: str):
        """
        Initialize dataset loader
        
        Args:
            dataset_dir: データセットディレクトリ
        """
        self.dataset_dir = Path(dataset_dir)
        self.metadata = self._load_metadata()
        self._chunk_files = None
        self._current_chunk = None
        self._current_chunk_idx = -1
    
    def _load_metadata(self) -> DatasetMetadata:
        """メタデータを読み込む"""
        metadata_path = self.dataset_dir / "metadata.json"
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata_dict = json.load(f)
            return DatasetMetadata(**metadata_dict)
    
    def __len__(self) -> int:
        """データセットのサイズを返す"""
        return self.metadata.num_tasks
    
    def __iter__(self) -> Iterator[Dict]:
        """イテレータとして使用"""
        return self.iter_batches(batch_size=1)
    
    def iter_batches(self, batch_size: int = 32, shuffle: bool = False) -> Iterator[List[Dict]]:
        """
        バッチ単位でデータを取得
        
        Args:
            batch_size: バッチサイズ
            shuffle: シャッフルするか
            
        Yields:
            バッチデータ
        """
        # チャンクファイルのリスト取得
        if self._chunk_files is None:
            self._chunk_files = sorted(
                self.dataset_dir.glob("data_chunk_*.jsonl*")
            ) + sorted(
                self.dataset_dir.glob("data_chunk_*.pkl*")
            )
        
        if not self._chunk_files:
            # 単一ファイルの場合
            data, _ = DatasetSerializer.load_dataset(str(self.dataset_dir))
            if shuffle:
                random.shuffle(data)
            
            for i in range(0, len(data), batch_size):
                yield data[i:i + batch_size]
        else:
            # チャンク単位で読み込み
            batch_buffer = []
            
            for chunk_file in self._chunk_files:
                # チャンクデータ読み込み
                chunk_data = self._load_chunk(chunk_file)
                
                if shuffle:
                    random.shuffle(chunk_data)
                
                # バッチ作成
                for item in chunk_data:
                    batch_buffer.append(item)
                    
                    if len(batch_buffer) >= batch_size:
                        yield batch_buffer[:batch_size]
                        batch_buffer = batch_buffer[batch_size:]
            
            # 残りのデータ
            if batch_buffer:
                yield batch_buffer
    
    def _load_chunk(self, chunk_file: Path) -> List[Dict]:
        """チャンクファイルを読み込む"""
        if chunk_file.suffix == '.gz':
            if '.jsonl' in chunk_file.name:
                with gzip.open(chunk_file, 'rt', encoding='utf-8') as f:
                    return [json.loads(line) for line in f]
            elif '.pkl' in chunk_file.name:
                with gzip.open(chunk_file, 'rb') as f:
                    return pickle.load(f)
        else:
            if chunk_file.suffix == '.jsonl':
                with open(chunk_file, 'r', encoding='utf-8') as f:
                    return [json.loads(line) for line in f]
            elif chunk_file.suffix == '.pkl':
                with open(chunk_file, 'rb') as f:
                    return pickle.load(f)
        
        return []
    
    def get_sample(self, n: int = 10, seed: int = None) -> List[Dict]:
        """
        データセットからサンプルを取得
        
        Args:
            n: サンプル数
            seed: ランダムシード
            
        Returns:
            サンプルデータ
        """
        if seed is not None:
            random.seed(seed)
        
        samples = []
        for batch in self.iter_batches(batch_size=min(n, 100)):
            samples.extend(batch)
            if len(samples) >= n:
                break
        
        return random.sample(samples, min(n, len(samples)))


# プリセットデータセット設定
PRESET_DATASETS = {
    "small": {
        "total_tasks": 10000,
        "description": "小規模データセット（テスト用）"
    },
    "medium": {
        "total_tasks": 50000,
        "description": "中規模データセット（開発用）"
    },
    "large": {
        "total_tasks": 100000,
        "description": "大規模データセット（本番学習用）"
    },
    "extra_large": {
        "total_tasks": 500000,
        "description": "超大規模データセット（高性能モデル用）"
    }
}


def generate_preset_dataset(
    preset: str,
    output_dir: str,
    task_type_distribution: Optional[Dict[str, float]] = None,
    difficulty_distribution: Optional[Dict[TaskDifficulty, float]] = None,
    **kwargs
) -> Tuple[str, DatasetMetadata]:
    """
    プリセットデータセットを生成
    
    Args:
        preset: プリセット名（small, medium, large, extra_large）
        output_dir: 出力ディレクトリ
        task_type_distribution: タスクタイプ分布
        difficulty_distribution: 難易度分布
        **kwargs: その他のパラメータ
        
    Returns:
        (出力ディレクトリ, メタデータ)のタプル
    """
    if preset not in PRESET_DATASETS:
        raise ValueError(f"Unknown preset: {preset}. Available: {list(PRESET_DATASETS.keys())}")
    
    preset_config = PRESET_DATASETS[preset]
    total_tasks = preset_config["total_tasks"]
    
    print(f"🎯 プリセットデータセット生成: {preset}")
    print(f"   {preset_config['description']}")
    
    # ジェネレータ初期化
    generator = LargeScaleDatasetGenerator()
    
    # データセット生成
    data, metadata = generator.generate_large_dataset(
        total_tasks=total_tasks,
        task_type_distribution=task_type_distribution,
        difficulty_distribution=difficulty_distribution,
        **kwargs
    )
    
    # 保存
    DatasetSerializer.save_dataset(
        data=data,
        metadata=metadata,
        output_dir=output_dir,
        format="jsonl",
        compress=True
    )
    
    return output_dir, metadata