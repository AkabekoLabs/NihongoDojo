"""
Dataset management for Nihongo DoJo
"""

from typing import List, Dict, Optional, Union, Callable
import json
import random
from pathlib import Path
from dataclasses import dataclass, asdict
from ..core import JapaneseTask, TaskType, TaskDifficulty
from ..tasks import (
    KanjiTask, ParticleTask, KeigoTask,
    WordOrderTask, CounterWordTask
)


@dataclass
class GRPOExample:
    """GRPO用の例データ"""
    instruction: str
    input: str
    output: str
    group_id: int
    task_id: str
    task_type: str
    difficulty: str
    reward: Optional[float] = None
    metadata: Optional[Dict] = None


class NihongoGRPODataset:
    """
    日本語GRPO学習用データセット
    """
    
    def __init__(self, tasks: Optional[List[JapaneseTask]] = None):
        """
        Initialize dataset
        
        Args:
            tasks: List of Japanese tasks
        """
        self.tasks = tasks or []
        self.groups = []
        self.task_generators = self._initialize_generators()
    
    def _initialize_generators(self) -> Dict[TaskType, Callable]:
        """タスクジェネレーターを初期化"""
        kanji = KanjiTask()
        particle = ParticleTask()
        keigo = KeigoTask()
        word_order = WordOrderTask()
        counter = CounterWordTask()
        
        return {
            TaskType.KANJI_READING: kanji.generate_reading_task,
            TaskType.KANJI_WRITING: kanji.generate_writing_task,
            TaskType.PARTICLE_FILL: particle.generate_particle_task,
            TaskType.KEIGO_CONVERSION: keigo.generate_keigo_task,
            TaskType.WORD_ORDER: word_order.generate_word_order_task,
            TaskType.COUNTER_WORD: counter.generate_counter_task,
        }
    
    def generate_tasks(self,
                      task_types: List[TaskType],
                      num_tasks: int,
                      difficulty_distribution: Optional[Dict[TaskDifficulty, float]] = None) -> List[JapaneseTask]:
        """
        指定されたタイプのタスクを生成
        
        Args:
            task_types: 生成するタスクタイプのリスト
            num_tasks: 生成するタスク数
            difficulty_distribution: 難易度の分布
        
        Returns:
            生成されたタスクのリスト
        """
        if difficulty_distribution is None:
            difficulty_distribution = {
                TaskDifficulty.BEGINNER: 0.3,
                TaskDifficulty.INTERMEDIATE: 0.4,
                TaskDifficulty.ADVANCED: 0.2,
                TaskDifficulty.NATIVE: 0.1
            }
        
        tasks = []
        difficulties = list(difficulty_distribution.keys())
        weights = list(difficulty_distribution.values())
        
        for _ in range(num_tasks):
            task_type = random.choice(task_types)
            difficulty = random.choices(difficulties, weights=weights)[0]
            
            generator = self.task_generators.get(task_type)
            if generator:
                try:
                    task = generator(difficulty)
                    tasks.append(task)
                except Exception as e:
                    print(f"Error generating task {task_type}: {e}")
        
        self.tasks.extend(tasks)
        return tasks
    
    def create_grpo_groups(self, group_size: int = 4, shuffle: bool = True) -> List[List[JapaneseTask]]:
        """
        GRPO用のタスクグループを作成
        
        Args:
            group_size: グループサイズ
            shuffle: タスクをシャッフルするか
        
        Returns:
            タスクグループのリスト
        """
        tasks = self.tasks.copy()
        if shuffle:
            random.shuffle(tasks)
        
        groups = []
        for i in range(0, len(tasks), group_size):
            group = tasks[i:i + group_size]
            if len(group) == group_size:  # 完全なグループのみ追加
                groups.append(group)
        
        self.groups = groups
        return groups
    
    def to_training_format(self, format_type: str = "alpaca") -> List[Dict]:
        """
        学習用フォーマットに変換
        
        Args:
            format_type: フォーマットタイプ（alpaca, chatgpt, etc.）
        
        Returns:
            学習用データのリスト
        """
        training_data = []
        
        for group_id, group in enumerate(self.groups):
            for task in group:
                if format_type == "alpaca":
                    example = {
                        "instruction": task.instruction,
                        "input": task.question,
                        "output": task.answer if isinstance(task.answer, str) else json.dumps(task.answer, ensure_ascii=False),
                        "group_id": group_id,
                        "task_id": task.id,
                        "task_type": task.type.value,
                        "difficulty": task.difficulty.value
                    }
                    
                    if task.context:
                        example["context"] = task.context
                    
                    if task.explanation:
                        example["explanation"] = task.explanation
                    
                    training_data.append(example)
                
                elif format_type == "chatgpt":
                    messages = [
                        {"role": "system", "content": task.instruction}
                    ]
                    
                    if task.context:
                        messages.append({"role": "system", "content": f"Context: {task.context}"})
                    
                    messages.append({"role": "user", "content": task.question})
                    messages.append({"role": "assistant", "content": task.answer if isinstance(task.answer, str) else json.dumps(task.answer, ensure_ascii=False)})
                    
                    example = {
                        "messages": messages,
                        "group_id": group_id,
                        "task_id": task.id,
                        "task_type": task.type.value,
                        "difficulty": task.difficulty.value
                    }
                    
                    training_data.append(example)
        
        return training_data
    
    def save(self, filepath: str, format_type: str = "json"):
        """
        データセットを保存
        
        Args:
            filepath: 保存先のファイルパス
            format_type: 保存形式（json, jsonl）
        """
        data = self.to_training_format()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            if format_type == "json":
                json.dump(data, f, ensure_ascii=False, indent=2)
            elif format_type == "jsonl":
                for item in data:
                    f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    def load(self, filepath: str):
        """
        データセットを読み込む
        
        Args:
            filepath: データセットファイルのパス
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            if filepath.endswith('.jsonl'):
                data = [json.loads(line) for line in f]
            else:
                data = json.load(f)
        
        # データからタスクを復元
        self.tasks = []
        for item in data:
            task = JapaneseTask(
                id=item.get('task_id', str(random.randint(1000000, 9999999))),
                type=TaskType(item['task_type']),
                difficulty=TaskDifficulty(item['difficulty']),
                instruction=item['instruction'],
                context=item.get('context'),
                question=item['input'],
                answer=item['output'],
                explanation=item.get('explanation'),
                metadata=item.get('metadata', {})
            )
            self.tasks.append(task)


def create_mixed_dataset(
    num_tasks_per_type: int = 100,
    task_types: Optional[List[TaskType]] = None,
    difficulty_distribution: Optional[Dict[TaskDifficulty, float]] = None,
    group_size: int = 4
) -> NihongoGRPODataset:
    """
    複数のタスクタイプを含む混合データセットを作成
    
    Args:
        num_tasks_per_type: 各タスクタイプごとのタスク数
        task_types: 含めるタスクタイプ（Noneの場合は全て）
        difficulty_distribution: 難易度分布
        group_size: GRPOグループサイズ
    
    Returns:
        作成されたデータセット
    """
    if task_types is None:
        task_types = [
            TaskType.KANJI_READING,
            TaskType.KANJI_WRITING,
            TaskType.PARTICLE_FILL,
            TaskType.KEIGO_CONVERSION,
            TaskType.WORD_ORDER,
            TaskType.COUNTER_WORD,
        ]
    
    dataset = NihongoGRPODataset()
    
    # 各タスクタイプごとにタスクを生成
    for task_type in task_types:
        dataset.generate_tasks(
            task_types=[task_type],
            num_tasks=num_tasks_per_type,
            difficulty_distribution=difficulty_distribution
        )
    
    # GRPOグループを作成
    dataset.create_grpo_groups(group_size=group_size, shuffle=True)
    
    return dataset


def load_preset_dataset(preset_name: str) -> NihongoGRPODataset:
    """
    プリセットデータセットを読み込む
    
    Args:
        preset_name: プリセット名（beginner, jlpt_n3, comprehensive等）
    
    Returns:
        プリセットデータセット
    """
    presets = {
        "beginner": {
            "task_types": [
                TaskType.KANJI_READING,
                TaskType.PARTICLE_FILL,
                TaskType.WORD_ORDER
            ],
            "difficulty_distribution": {
                TaskDifficulty.BEGINNER: 0.8,
                TaskDifficulty.INTERMEDIATE: 0.2,
                TaskDifficulty.ADVANCED: 0.0,
                TaskDifficulty.NATIVE: 0.0
            },
            "num_tasks_per_type": 50
        },
        "jlpt_n3": {
            "task_types": [
                TaskType.KANJI_READING,
                TaskType.KANJI_WRITING,
                    TaskType.PARTICLE_FILL,
                TaskType.KEIGO_CONVERSION
            ],
            "difficulty_distribution": {
                TaskDifficulty.BEGINNER: 0.2,
                TaskDifficulty.INTERMEDIATE: 0.6,
                TaskDifficulty.ADVANCED: 0.2,
                TaskDifficulty.NATIVE: 0.0
            },
            "num_tasks_per_type": 100
        },
        "comprehensive": {
            "task_types": None,  # All types
            "difficulty_distribution": {
                TaskDifficulty.BEGINNER: 0.25,
                TaskDifficulty.INTERMEDIATE: 0.35,
                TaskDifficulty.ADVANCED: 0.25,
                TaskDifficulty.NATIVE: 0.15
            },
            "num_tasks_per_type": 200
        }
    }
    
    if preset_name not in presets:
        raise ValueError(f"Unknown preset: {preset_name}. Available presets: {list(presets.keys())}")
    
    preset = presets[preset_name]
    
    return create_mixed_dataset(
        num_tasks_per_type=preset["num_tasks_per_type"],
        task_types=preset["task_types"],
        difficulty_distribution=preset["difficulty_distribution"]
    )