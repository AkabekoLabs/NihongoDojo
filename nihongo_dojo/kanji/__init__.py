"""
Nihongo DoJo 漢字モジュール

常用漢字データとその処理機能を提供
"""

from .joyo_kanji_complete import (
    # データ
    ALL_JOYO_KANJI,
    ELEMENTARY_KANJI,
    JUNIOR_HIGH_KANJI,
    GRADE_KANJI_MAP,
    
    # 関数
    get_kanji_by_grade,
    get_kanji_by_grades,
    get_kanji_by_level,
    get_all_joyo_kanji,
    search_kanji,
    get_kanji_stats,
)

# 複合語データのインポート
from .compound_words import COMPOUND_WORDS_BY_GRADE

# 個別学年データのインポート（必要に応じて）
from .kanji_grade_1 import GRADE_1_KANJI
from .kanji_grade_2 import GRADE_2_KANJI
from .kanji_grade_3 import GRADE_3_KANJI
from .kanji_grade_4 import GRADE_4_KANJI
from .kanji_grade_5 import GRADE_5_KANJI
from .kanji_grade_6 import GRADE_6_KANJI
from .kanji_junior_high_1 import JUNIOR_HIGH_1_KANJI
from .kanji_junior_high_2 import JUNIOR_HIGH_2_KANJI
from .kanji_junior_high_3 import JUNIOR_HIGH_3_KANJI

__all__ = [
    # 統合データ
    'ALL_JOYO_KANJI',
    'ELEMENTARY_KANJI',
    'JUNIOR_HIGH_KANJI',
    'GRADE_KANJI_MAP',
    
    # 個別学年データ
    'GRADE_1_KANJI',
    'GRADE_2_KANJI',
    'GRADE_3_KANJI',
    'GRADE_4_KANJI',
    'GRADE_5_KANJI',
    'GRADE_6_KANJI',
    'JUNIOR_HIGH_1_KANJI',
    'JUNIOR_HIGH_2_KANJI',
    'JUNIOR_HIGH_3_KANJI',
    
    # 関数
    'get_kanji_by_grade',
    'get_kanji_by_grades',
    'get_kanji_by_level',
    'get_all_joyo_kanji',
    'search_kanji',
    'get_kanji_stats',
    
    # 複合語データ
    'COMPOUND_WORDS_BY_GRADE',
]

# モジュール情報
__version__ = '1.0.0'
__author__ = 'Nihongo DoJo Team'