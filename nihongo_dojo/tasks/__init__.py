"""
Task modules for Nihongo DoJo
"""

# Basic tasks
from .tasks import (
    KanjiTask,
    KeigoTask,
    WordOrderTask,
    ParticleTask,
    CounterWordTask
)

# Advanced tasks
from .advanced_tasks import (
    AdvancedGrammarTask,
    OnomatopoeiaTask,
    ConversationTask,
    ProverbIdiomTask,
    BusinessJapaneseTask,
    ClassicalJapaneseTask,
    SpecializedVocabularyTask
)

# Cultural tasks
from .cultural_tasks import (
    SeasonalExpressionTask,
    HonorificsTask,
    SocialContextTask,
    RegionalDialectTask,
    AgeGenderLanguageTask,
    EmotionalExpressionTask
)

# Complete kanji tasks
from .complete_kanji_tasks import CompleteKanjiTask

__all__ = [
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
    
    # Complete Kanji
    "CompleteKanjiTask"
]