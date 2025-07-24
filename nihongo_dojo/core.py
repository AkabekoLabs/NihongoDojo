"""
Core module for Nihongo DoJo
"""

from typing import Dict, List, Optional, Union, Tuple, Any
import json
import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class TaskDifficulty(Enum):
    """タスクの難易度レベル"""
    BEGINNER = "beginner"      # N5-N4レベル
    INTERMEDIATE = "intermediate"  # N3レベル
    ADVANCED = "advanced"       # N2-N1レベル
    NATIVE = "native"          # ネイティブレベル


class TaskType(Enum):
    """タスクタイプの定義"""
    # 基本タスク
    KANJI_READING = "kanji_reading"
    KANJI_WRITING = "kanji_writing"
    PARTICLE_FILL = "particle_fill"
    WORD_ORDER = "word_order"
    KEIGO_CONVERSION = "keigo_conversion"
    COUNTER_WORD = "counter_word"
    COMPOSITION = "composition"
    
    # 拡張タスク
    ONOMATOPOEIA = "onomatopoeia"
    CONVERSATION = "conversation"
    PROVERB_IDIOM = "proverb_idiom"
    BUSINESS_JAPANESE = "business_japanese"
    CLASSICAL_JAPANESE = "classical_japanese"
    SPECIALIZED_VOCABULARY = "specialized_vocabulary"
    
    # 文化的タスク
    SEASONAL_EXPRESSION = "seasonal_expression"
    SOCIAL_CONTEXT = "social_context"
    REGIONAL_DIALECT = "regional_dialect"
    AGE_GENDER_LANGUAGE = "age_gender_language"
    EMOTIONAL_EXPRESSION = "emotional_expression"
    ADVANCED_GRAMMAR = "advanced_grammar"


@dataclass
class JapaneseTask:
    """日本語タスクの基本データ構造"""
    id: str
    type: TaskType
    difficulty: TaskDifficulty
    instruction: str
    context: Optional[str]
    question: str
    answer: Union[str, List[str]]
    explanation: Optional[str]
    metadata: Dict


class NihongoDoJo:
    """
    Nihongo DoJo - 日本語学習用GRPOシステムのメインクラス
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize Nihongo DoJo
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or self._default_config()
        self.tasks = []
        self.task_generators = {}
        self._initialize_generators()
    
    def _default_config(self) -> Dict:
        """デフォルト設定を返す"""
        return {
            "group_size": 4,
            "reward_weights": {
                "correctness": 0.4,
                "fluency": 0.3,
                "appropriateness": 0.2,
                "creativity": 0.1
            },
            "difficulty_distribution": {
                TaskDifficulty.BEGINNER: 0.3,
                TaskDifficulty.INTERMEDIATE: 0.4,
                TaskDifficulty.ADVANCED: 0.2,
                TaskDifficulty.NATIVE: 0.1
            }
        }
    
    def _initialize_generators(self):
        """タスクジェネレーターを初期化"""
        try:
            from .tasks import (
                KanjiTask, ParticleTask, KeigoTask,
                WordOrderTask, CounterWordTask,
                AdvancedGrammarTask, OnomatopoeiaTask, ConversationTask, ProverbIdiomTask,
                BusinessJapaneseTask, ClassicalJapaneseTask, SpecializedVocabularyTask,
                SeasonalExpressionTask, HonorificsTask, SocialContextTask, RegionalDialectTask,
                AgeGenderLanguageTask, EmotionalExpressionTask
            )
        except ImportError as e:
            raise ImportError(f"Failed to import task modules: {e}. "
                            f"Please ensure all dependencies are installed.")
        
        # Import cultural tasks separately to handle optional dependencies
        try:
            from .tasks.cultural_tasks import HonorificsTask
        except ImportError:
            # Use the basic tasks version if cultural_tasks is not available
            pass
        
        # 基本タスクのインスタンス化
        kanji = KanjiTask()
        particle = ParticleTask()
        keigo = KeigoTask()
        word_order = WordOrderTask()
        counter = CounterWordTask()
        
        # 拡張タスクのインスタンス化
        advanced_grammar = AdvancedGrammarTask()
        onomatopoeia = OnomatopoeiaTask()
        conversation = ConversationTask()
        proverb_idiom = ProverbIdiomTask()
        business = BusinessJapaneseTask()
        classical = ClassicalJapaneseTask()
        specialized = SpecializedVocabularyTask()
        
        # 文化的タスクのインスタンス化
        seasonal = SeasonalExpressionTask()
        social = SocialContextTask()
        regional = RegionalDialectTask()
        age_gender = AgeGenderLanguageTask()
        emotional = EmotionalExpressionTask()
        
        # タスクジェネレーターのマッピング
        self.task_generators = {
            TaskType.KANJI_READING: kanji.generate_reading_task,
            TaskType.KANJI_WRITING: kanji.generate_writing_task,
            TaskType.PARTICLE_FILL: particle.generate_particle_task,
            TaskType.KEIGO_CONVERSION: keigo.generate_keigo_task,
            TaskType.WORD_ORDER: word_order.generate_word_order_task,
            TaskType.COUNTER_WORD: counter.generate_counter_task,
            TaskType.ADVANCED_GRAMMAR: advanced_grammar.generate_pattern_transformation_task,
            TaskType.ONOMATOPOEIA: onomatopoeia.generate_onomatopoeia_task,
            TaskType.CONVERSATION: conversation.generate_conversation_task,
            TaskType.PROVERB_IDIOM: proverb_idiom.generate_proverb_task,
            TaskType.BUSINESS_JAPANESE: business.generate_business_task,
            TaskType.CLASSICAL_JAPANESE: classical.generate_classical_task,
            TaskType.SPECIALIZED_VOCABULARY: specialized.generate_vocabulary_task,
            TaskType.SEASONAL_EXPRESSION: seasonal.generate_seasonal_task,
            TaskType.SOCIAL_CONTEXT: social.generate_social_context_task,
            TaskType.REGIONAL_DIALECT: regional.generate_dialect_task,
            TaskType.AGE_GENDER_LANGUAGE: age_gender.generate_age_gender_task,
            TaskType.EMOTIONAL_EXPRESSION: emotional.generate_emotion_task
        }
    
    def generate_task(self, 
                     task_type: TaskType, 
                     difficulty: Optional[TaskDifficulty] = None,
                     **kwargs: Any) -> JapaneseTask:
        """
        指定されたタイプのタスクを生成
        
        Args:
            task_type: タスクのタイプ
            difficulty: 難易度（指定しない場合はランダム）
            **kwargs: タスク固有のパラメータ
        
        Returns:
            生成されたタスク
        """
        if difficulty is None:
            difficulty = self._sample_difficulty()
        
        generator = self.task_generators.get(task_type)
        if generator is None:
            raise ValueError(f"Unknown task type: {task_type}")
        
        return generator(difficulty, **kwargs)
    
    def _sample_difficulty(self) -> TaskDifficulty:
        """設定に基づいて難易度をサンプリング"""
        distribution = self.config["difficulty_distribution"]
        difficulties = list(distribution.keys())
        weights = list(distribution.values())
        return random.choices(difficulties, weights=weights)[0]
    
    def create_grpo_groups(self, 
                          num_groups: int,
                          task_types: Optional[List[TaskType]] = None) -> List[List[JapaneseTask]]:
        """
        GRPO用のタスクグループを作成
        
        Args:
            num_groups: 作成するグループ数
            task_types: 使用するタスクタイプ（指定しない場合は全て）
        
        Returns:
            タスクグループのリスト
        """
        if task_types is None:
            task_types = list(TaskType)
        
        group_size = self.config["group_size"]
        groups = []
        
        for _ in range(num_groups):
            group = []
            for _ in range(group_size):
                task_type = random.choice(task_types)
                task = self.generate_task(task_type)
                group.append(task)
            groups.append(group)
        
        return groups
    
    def export_dataset(self, 
                      groups: List[List[JapaneseTask]], 
                      filepath: Union[str, Path],
                      format: str = "json") -> None:
        """
        データセットをファイルにエクスポート
        
        Args:
            groups: タスクグループ
            filepath: 保存先のファイルパス
            format: 出力フォーマット（json, jsonl）
        """
        # パストラバーサル対策
        from pathlib import Path
        filepath = Path(filepath).resolve()
        
        # ファイル拡張子の検証
        allowed_extensions = {'.json', '.jsonl'}
        if filepath.suffix not in allowed_extensions:
            raise ValueError(f"Invalid file extension. Allowed: {allowed_extensions}")
        if format == "json":
            data = []
            for group_idx, group in enumerate(groups):
                for task in group:
                    entry = {
                        "group_id": group_idx,
                        "task_id": task.id,
                        "type": task.type.value,
                        "difficulty": task.difficulty.value,
                        "instruction": task.instruction,
                        "context": task.context,
                        "question": task.question,
                        "answer": task.answer,
                        "explanation": task.explanation,
                        "metadata": task.metadata
                    }
                    data.append(entry)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        
        elif format == "jsonl":
            with open(filepath, 'w', encoding='utf-8') as f:
                for group_idx, group in enumerate(groups):
                    for task in group:
                        entry = {
                            "group_id": group_idx,
                            "task_id": task.id,
                            "type": task.type.value,
                            "difficulty": task.difficulty.value,
                            "instruction": task.instruction,
                            "context": task.context,
                            "question": task.question,
                            "answer": task.answer,
                            "explanation": task.explanation,
                            "metadata": task.metadata
                        }
                        f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def load_dataset(self, filepath: Union[str, Path]) -> List[List[JapaneseTask]]:
        """
        ファイルからデータセットを読み込む
        
        Args:
            filepath: データセットファイルのパス
        
        Returns:
            タスクグループのリスト
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            if filepath.endswith('.jsonl'):
                data = [json.loads(line) for line in f]
            else:
                data = json.load(f)
        
        # Group by group_id
        groups_dict = {}
        for entry in data:
            group_id = entry['group_id']
            if group_id not in groups_dict:
                groups_dict[group_id] = []
            
            task = JapaneseTask(
                id=entry['task_id'],
                type=TaskType(entry['type']),
                difficulty=TaskDifficulty(entry['difficulty']),
                instruction=entry['instruction'],
                context=entry['context'],
                question=entry['question'],
                answer=entry['answer'],
                explanation=entry['explanation'],
                metadata=entry['metadata']
            )
            groups_dict[group_id].append(task)
        
        return [groups_dict[i] for i in sorted(groups_dict.keys())]