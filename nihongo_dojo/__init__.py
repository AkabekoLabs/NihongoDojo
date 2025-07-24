"""
Nihongo DoJo - A GRPO Dataset Library for Japanese Language Training
日本語DoJo - 日本語学習用GRPOデータセットライブラリ
"""

from .core import NihongoDoJo, TaskType, TaskDifficulty, JapaneseTask
from .tasks import (
    # Basic Tasks
    KanjiTask,
    KeigoTask,
    WordOrderTask,
    ParticleTask,
    CounterWordTask,
    # Advanced Tasks
    AdvancedGrammarTask,
    OnomatopoeiaTask,
    ConversationTask,
    ProverbIdiomTask,
    BusinessJapaneseTask,
    ClassicalJapaneseTask,
    SpecializedVocabularyTask,
    # Cultural Tasks
    SeasonalExpressionTask,
    HonorificsTask,
    SocialContextTask,
    RegionalDialectTask,
    AgeGenderLanguageTask,
    EmotionalExpressionTask,
    # Complete Kanji Tasks
    CompleteKanjiTask
)
from .data.datasets import (
    NihongoGRPODataset,
    create_mixed_dataset,
    load_preset_dataset
)
from .data.dataset_builder import (
    load_dataset,
    load_small_dataset,
    load_medium_dataset,
    load_large_dataset,
    load_extra_large_dataset,
    NihongoDojoDatasetHub,
    create_all_preset_datasets
)
from .data.large_scale_datasets import (
    LargeScaleDatasetGenerator,
    DatasetLoader,
    DatasetSerializer,
    generate_preset_dataset
)
from .data.huggingface_dataset_builder import HuggingFaceDatasetBuilder
from .kanji import (
    get_kanji_by_grade,
    get_kanji_by_grades,
    search_kanji,
    get_kanji_stats,
    COMPOUND_WORDS_BY_GRADE,
    ALL_JOYO_KANJI
)

__version__ = "1.0.0"
__author__ = "Nihongo DoJo Team"

__all__ = [
    # Core
    "NihongoDoJo",
    "TaskType",
    "TaskDifficulty",
    "JapaneseTask",
    
    # Basic Tasks
    "KanjiTask",
    "KeigoTask",
    "WordOrderTask",
    "ParticleTask",
    "CounterWordTask",
    
    # Advanced Tasks
    "AdvancedGrammarTask",
    "OnomatopoeiaTask",
    "ConversationTask",
    "ProverbIdiomTask",
    "BusinessJapaneseTask",
    "ClassicalJapaneseTask",
    "SpecializedVocabularyTask",
    
    # Cultural Tasks
    "SeasonalExpressionTask",
    "HonorificsTask",
    "SocialContextTask",
    "RegionalDialectTask",
    "AgeGenderLanguageTask",
    "EmotionalExpressionTask",
    
    # Complete Kanji Tasks
    "CompleteKanjiTask",
    
    # Dataset & Generation
    "NihongoGRPODataset",
    "create_mixed_dataset",
    "load_preset_dataset",
    "LargeScaleDatasetGenerator",
    "DatasetLoader",
    "DatasetSerializer",
    "generate_preset_dataset",
    
    # Dataset Loading
    "load_dataset",
    "load_small_dataset",
    "load_medium_dataset", 
    "load_large_dataset",
    "load_extra_large_dataset",
    "create_all_preset_datasets",
    "NihongoDojoDatasetHub",
    
    # Kanji Functions
    "get_kanji_by_grade",
    "get_kanji_by_grades",
    "search_kanji",
    "get_kanji_stats",
    "COMPOUND_WORDS_BY_GRADE",
    "ALL_JOYO_KANJI",
    
    # Hugging Face Integration
    "HuggingFaceDatasetBuilder"
]

# Training and Reward utilities (from subdirectories)
try:
    from .colab import (
        GRPOVisualizationCallback,
        TrainingLogger,
        LoggingRewardWrapper,
        plot_training_history,
        setup_japanese_font,
        check_gpu_environment
    )
    __all__.extend([
        "GRPOVisualizationCallback",
        "TrainingLogger",
        "LoggingRewardWrapper",
        "plot_training_history",
        "setup_japanese_font",
        "check_gpu_environment"
    ])
except ImportError as e:
    import warnings
    warnings.warn(f"Optional colab module not available: {e}")

try:
    from .reward import JapaneseTaskRewardFunctions
    __all__.extend(["JapaneseTaskRewardFunctions"])
except ImportError as e:
    import warnings
    warnings.warn(f"Optional reward module not available: {e}")