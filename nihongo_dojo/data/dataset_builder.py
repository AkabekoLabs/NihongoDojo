"""
Dataset builder and management interface for Nihongo DoJo
Provides easy-to-use APIs for loading pre-generated datasets
"""

import os
import json
import requests
from typing import Dict, List, Optional, Union, Tuple
from pathlib import Path
from tqdm import tqdm
import hashlib
from urllib.parse import urljoin

from .large_scale_datasets import (
    DatasetLoader, 
    DatasetSerializer,
    DatasetMetadata,
    generate_preset_dataset,
    PRESET_DATASETS
)


class NihongoDojoDatasetHub:
    """
    Nihongo DoJoデータセットのハブ
    事前生成されたデータセットへの簡単なアクセスを提供
    """
    
    # データセットリポジトリURL（実際のデプロイ時に更新）
    DEFAULT_REPO_URL = "https://huggingface.co/datasets/nihongo-dojo/grpo-datasets/resolve/main/"
    
    # 利用可能なデータセット
    AVAILABLE_DATASETS = {
        "nihongo-dojo-10k": {
            "size": 10000,
            "description": "基本的な10,000タスクのデータセット（テスト・開発用）",
            "url": "nihongo-dojo-10k.tar.gz",
            "checksum": "placeholder_checksum_10k",
            "compressed_size": "~50MB"
        },
        "nihongo-dojo-50k": {
            "size": 50000,
            "description": "中規模50,000タスクのデータセット（小規模モデル学習用）",
            "url": "nihongo-dojo-50k.tar.gz",
            "checksum": "placeholder_checksum_50k",
            "compressed_size": "~250MB"
        },
        "nihongo-dojo-100k": {
            "size": 100000,
            "description": "標準100,000タスクのデータセット（推奨）",
            "url": "nihongo-dojo-100k.tar.gz",
            "checksum": "placeholder_checksum_100k",
            "compressed_size": "~500MB"
        },
        "nihongo-dojo-500k": {
            "size": 500000,
            "description": "大規模500,000タスクのデータセット（高性能モデル用）",
            "url": "nihongo-dojo-500k.tar.gz",
            "checksum": "placeholder_checksum_500k",
            "compressed_size": "~2.5GB"
        },
        "nihongo-dojo-beginner": {
            "size": 100000,
            "description": "初級レベル特化データセット",
            "url": "nihongo-dojo-beginner-100k.tar.gz",
            "checksum": "placeholder_checksum_beginner",
            "compressed_size": "~400MB"
        },
        "nihongo-dojo-business": {
            "size": 50000,
            "description": "ビジネス日本語特化データセット",
            "url": "nihongo-dojo-business-50k.tar.gz",
            "checksum": "placeholder_checksum_business",
            "compressed_size": "~300MB"
        }
    }
    
    def __init__(self, cache_dir: Optional[str] = None, repo_url: Optional[str] = None):
        """
        Initialize dataset hub
        
        Args:
            cache_dir: キャッシュディレクトリ（デフォルト: ~/.cache/nihongo_dojo）
            repo_url: データセットリポジトリURL
        """
        self.cache_dir = Path(cache_dir or os.path.expanduser("~/.cache/nihongo_dojo"))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.repo_url = repo_url or self.DEFAULT_REPO_URL
    
    def list_datasets(self) -> Dict[str, Dict]:
        """利用可能なデータセット一覧を取得"""
        return self.AVAILABLE_DATASETS.copy()
    
    def load_dataset(
        self,
        name: str,
        force_download: bool = False,
        verify_checksum: bool = True
    ) -> DatasetLoader:
        """
        データセットを読み込む
        
        Args:
            name: データセット名
            force_download: 強制的に再ダウンロードするか
            verify_checksum: チェックサムを検証するか
            
        Returns:
            DatasetLoader インスタンス
        """
        if name not in self.AVAILABLE_DATASETS:
            raise ValueError(f"Unknown dataset: {name}. Available: {list(self.AVAILABLE_DATASETS.keys())}")
        
        dataset_info = self.AVAILABLE_DATASETS[name]
        dataset_path = self.cache_dir / name
        
        # ダウンロードが必要か確認
        if force_download or not dataset_path.exists():
            self._download_dataset(name, dataset_info, verify_checksum)
        
        # データセットローダーを返す
        return DatasetLoader(str(dataset_path))
    
    def _download_dataset(
        self,
        name: str,
        dataset_info: Dict,
        verify_checksum: bool = True
    ):
        """データセットをダウンロード"""
        import tarfile
        
        dataset_url = urljoin(self.repo_url, dataset_info["url"])
        dataset_path = self.cache_dir / name
        archive_path = self.cache_dir / f"{name}.tar.gz"
        
        print(f"📥 データセットをダウンロード中: {name}")
        print(f"   URL: {dataset_url}")
        print(f"   サイズ: {dataset_info['compressed_size']}")
        
        # ダウンロード
        response = requests.get(dataset_url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(archive_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True, desc="ダウンロード") as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        # チェックサム検証
        if verify_checksum:
            print("🔍 チェックサム検証中...")
            calculated_checksum = self._calculate_checksum(archive_path)
            if calculated_checksum != dataset_info["checksum"]:
                os.remove(archive_path)
                raise ValueError(f"Checksum mismatch for {name}")
        
        # 解凍
        print("📦 解凍中...")
        with tarfile.open(archive_path, 'r:gz') as tar:
            tar.extractall(self.cache_dir)
        
        # アーカイブ削除
        os.remove(archive_path)
        
        print(f"✅ データセットの準備完了: {dataset_path}")
    
    def _calculate_checksum(self, filepath: Path) -> str:
        """ファイルのチェックサムを計算"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def get_dataset_info(self, name: str) -> Dict:
        """データセットの詳細情報を取得"""
        if name not in self.AVAILABLE_DATASETS:
            raise ValueError(f"Unknown dataset: {name}")
        
        info = self.AVAILABLE_DATASETS[name].copy()
        dataset_path = self.cache_dir / name
        
        # ローカルに存在するか確認
        if dataset_path.exists():
            info["local_path"] = str(dataset_path)
            info["is_downloaded"] = True
            
            # メタデータ読み込み
            try:
                metadata_path = dataset_path / "metadata.json"
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    info["metadata"] = metadata
            except:
                pass
        else:
            info["is_downloaded"] = False
        
        return info


def load_dataset(
    name: str = "nihongo-dojo-100k",
    cache_dir: Optional[str] = None,
    streaming: bool = False,
    batch_size: int = 32
) -> Union[DatasetLoader, 'StreamingDataset']:
    """
    Nihongo DoJoデータセットを読み込む便利関数
    
    Args:
        name: データセット名
        cache_dir: キャッシュディレクトリ
        streaming: ストリーミングモードで読み込むか
        batch_size: バッチサイズ（ストリーミング時）
        
    Returns:
        DatasetLoaderまたはStreamingDatasetインスタンス
        
    Example:
        >>> # 標準的な使い方
        >>> dataset = load_dataset("nihongo-dojo-100k")
        >>> for batch in dataset.iter_batches(batch_size=32):
        ...     # バッチ処理
        ...     pass
        
        >>> # ストリーミングモード
        >>> dataset = load_dataset("nihongo-dojo-100k", streaming=True)
        >>> for batch in dataset:
        ...     # バッチ処理
        ...     pass
    """
    hub = NihongoDojoDatasetHub(cache_dir=cache_dir)
    
    if streaming:
        return StreamingDataset(hub, name, batch_size)
    else:
        return hub.load_dataset(name)


class StreamingDataset:
    """ストリーミング用データセットラッパー"""
    
    def __init__(self, hub: NihongoDojoDatasetHub, name: str, batch_size: int = 32):
        self.hub = hub
        self.name = name
        self.batch_size = batch_size
        self._loader = None
    
    def __iter__(self):
        """イテレータを返す"""
        if self._loader is None:
            self._loader = self.hub.load_dataset(self.name)
        return self._loader.iter_batches(batch_size=self.batch_size, shuffle=True)
    
    def __len__(self):
        """データセットサイズを返す"""
        if self._loader is None:
            self._loader = self.hub.load_dataset(self.name)
        return len(self._loader)


# データセット生成スクリプト
def create_all_preset_datasets(output_base_dir: str = "./datasets"):
    """
    全てのプリセットデータセットを生成
    
    Args:
        output_base_dir: 出力ベースディレクトリ
    """
    from .large_scale_datasets import LargeScaleDatasetGenerator, DatasetSerializer
    
    # 生成設定
    configs = {
        "nihongo-dojo-10k": {
            "total_tasks": 10000,
            "task_type_distribution": {'basic': 0.7, 'advanced': 0.2, 'cultural': 0.1}
        },
        "nihongo-dojo-50k": {
            "total_tasks": 50000,
            "task_type_distribution": {'basic': 0.6, 'advanced': 0.3, 'cultural': 0.1}
        },
        "nihongo-dojo-100k": {
            "total_tasks": 100000,
            "task_type_distribution": {'basic': 0.6, 'advanced': 0.3, 'cultural': 0.1}
        },
        "nihongo-dojo-500k": {
            "total_tasks": 500000,
            "task_type_distribution": {'basic': 0.5, 'advanced': 0.35, 'cultural': 0.15}
        },
        "nihongo-dojo-beginner": {
            "total_tasks": 100000,
            "task_type_distribution": {'basic': 0.9, 'advanced': 0.1, 'cultural': 0.0},
            "difficulty_distribution": {
                "beginner": 0.7,
                "intermediate": 0.3,
                "advanced": 0.0,
                "native": 0.0
            }
        },
        "nihongo-dojo-business": {
            "total_tasks": 50000,
            "task_type_distribution": {'basic': 0.2, 'advanced': 0.7, 'cultural': 0.1},
            "focus_tasks": ["business_japanese", "keigo_conversion", "formal_writing"]
        }
    }
    
    generator = LargeScaleDatasetGenerator()
    
    for name, config in configs.items():
        print(f"\n{'='*70}")
        print(f"🎯 生成開始: {name}")
        print(f"{'='*70}")
        
        output_dir = os.path.join(output_base_dir, name)
        
        # データセット生成
        data, metadata = generator.generate_large_dataset(**config)
        
        # 保存
        DatasetSerializer.save_dataset(
            data=data,
            metadata=metadata,
            output_dir=output_dir,
            format="jsonl",
            compress=True
        )
        
        # アーカイブ作成
        import tarfile
        archive_path = f"{output_dir}.tar.gz"
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(output_dir, arcname=name)
        
        print(f"✅ アーカイブ作成完了: {archive_path}")
        
        # チェックサム計算
        checksum = hashlib.sha256()
        with open(archive_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                checksum.update(chunk)
        
        print(f"📝 チェックサム: {checksum.hexdigest()}")


# 簡易アクセス用のショートカット
def load_small_dataset(**kwargs):
    """小規模データセット（10k）を読み込む"""
    return load_dataset("nihongo-dojo-10k", **kwargs)


def load_medium_dataset(**kwargs):
    """中規模データセット（50k）を読み込む"""
    return load_dataset("nihongo-dojo-50k", **kwargs)


def load_large_dataset(**kwargs):
    """大規模データセット（100k）を読み込む"""
    return load_dataset("nihongo-dojo-100k", **kwargs)


def load_extra_large_dataset(**kwargs):
    """超大規模データセット（500k）を読み込む"""
    return load_dataset("nihongo-dojo-500k", **kwargs)