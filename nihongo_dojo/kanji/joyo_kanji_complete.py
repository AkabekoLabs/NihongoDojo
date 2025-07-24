#!/usr/bin/env python
"""
完全な常用漢字データ - 統合ファイル
各学年の漢字データをインポートして統合
"""

# 小学校各学年の漢字をインポート
from .kanji_grade_1 import GRADE_1_KANJI as KANJI_GRADE_1
from .kanji_grade_2 import GRADE_2_KANJI as KANJI_GRADE_2
from .kanji_grade_3 import GRADE_3_KANJI as KANJI_GRADE_3
from .kanji_grade_4 import GRADE_4_KANJI as KANJI_GRADE_4
from .kanji_grade_5 import GRADE_5_KANJI as KANJI_GRADE_5
from .kanji_grade_6 import GRADE_6_KANJI as KANJI_GRADE_6

# 中学校各学年の漢字をインポート
from .kanji_junior_high_1 import JUNIOR_HIGH_1_KANJI as KANJI_JUNIOR_HIGH_1
from .kanji_junior_high_2 import JUNIOR_HIGH_2_KANJI as KANJI_JUNIOR_HIGH_2
from .kanji_junior_high_3 import JUNIOR_HIGH_3_KANJI as KANJI_JUNIOR_HIGH_3

# その他の漢字をインポート
from .kanji_others import OTHER_KANJI as KANJI_OTHERS

# 統合された常用漢字リスト
ALL_JOYO_KANJI = (
    KANJI_GRADE_1 + 
    KANJI_GRADE_2 + 
    KANJI_GRADE_3 + 
    KANJI_GRADE_4 + 
    KANJI_GRADE_5 + 
    KANJI_GRADE_6 + 
    KANJI_JUNIOR_HIGH_1 + 
    KANJI_JUNIOR_HIGH_2 + 
    KANJI_JUNIOR_HIGH_3 + 
    KANJI_OTHERS
)

# 学年マッピング
GRADE_KANJI_MAP = {
    1: KANJI_GRADE_1,
    2: KANJI_GRADE_2,
    3: KANJI_GRADE_3,
    4: KANJI_GRADE_4,
    5: KANJI_GRADE_5,
    6: KANJI_GRADE_6,
    7: KANJI_JUNIOR_HIGH_1,  # 中学1年
    8: KANJI_JUNIOR_HIGH_2,  # 中学2年
    9: KANJI_JUNIOR_HIGH_3,  # 中学3年
    10: KANJI_OTHERS,        # その他
}

# 小学校の漢字（教育漢字）
ELEMENTARY_KANJI = (
    KANJI_GRADE_1 + 
    KANJI_GRADE_2 + 
    KANJI_GRADE_3 + 
    KANJI_GRADE_4 + 
    KANJI_GRADE_5 + 
    KANJI_GRADE_6
)

# 中学校の漢字
JUNIOR_HIGH_KANJI = (
    KANJI_JUNIOR_HIGH_1 + 
    KANJI_JUNIOR_HIGH_2 + 
    KANJI_JUNIOR_HIGH_3
)


def tuple_to_dict(kanji_tuple):
    """
    タプル形式の漢字データを辞書形式に変換
    
    Args:
        kanji_tuple: (漢字, 音読み, 訓読み, 意味, 学年, 画数)
    
    Returns:
        dict: 辞書形式の漢字データ
    """
    if len(kanji_tuple) >= 6:
        return {
            "kanji": kanji_tuple[0],
            "on_yomi": kanji_tuple[1] if kanji_tuple[1] else [],
            "kun_yomi": kanji_tuple[2] if kanji_tuple[2] else [],
            "meanings": kanji_tuple[3] if kanji_tuple[3] else [],
            "grade": kanji_tuple[4],
            "stroke_count": kanji_tuple[5]
        }
    return None


def get_kanji_by_grade(grade, as_dict=True):
    """
    学年別の漢字を取得
    
    Args:
        grade (int): 学年 (1-6: 小学校, 7-9: 中学校, 10: その他)
        as_dict (bool): True の場合、辞書形式で返す
    
    Returns:
        list: 指定学年の漢字リスト
    """
    kanji_list = GRADE_KANJI_MAP.get(grade, [])
    if as_dict:
        return [tuple_to_dict(k) for k in kanji_list if tuple_to_dict(k)]
    return kanji_list


def get_kanji_by_grades(grades, as_dict=True):
    """
    複数学年の漢字を取得
    
    Args:
        grades (list): 学年のリスト
        as_dict (bool): True の場合、辞書形式で返す
    
    Returns:
        list: 指定学年の漢字を結合したリスト
    """
    result = []
    for grade in grades:
        result.extend(get_kanji_by_grade(grade, as_dict=as_dict))
    return result


def get_kanji_by_level(level):
    """
    レベル別の漢字を取得
    
    Args:
        level (str): "elementary", "junior_high", "all"
    
    Returns:
        list: 指定レベルの漢字リスト
    """
    if level == "elementary":
        return ELEMENTARY_KANJI
    elif level == "junior_high":
        return JUNIOR_HIGH_KANJI
    elif level == "all":
        return ALL_JOYO_KANJI
    else:
        return []


def get_all_joyo_kanji(as_dict=True):
    """
    全ての常用漢字を取得
    
    Args:
        as_dict (bool): True の場合は辞書形式、False の場合はタプル形式
    
    Returns:
        list: 全ての常用漢字のリスト
    """
    if as_dict:
        return [
            {
                "kanji": kanji[0],
                "on_readings": kanji[1],
                "kun_readings": kanji[2],
                "meanings": kanji[3],
                "grade": kanji[4],
                "stroke_count": kanji[5]
            }
            for kanji in ALL_JOYO_KANJI
        ]
    else:
        return ALL_JOYO_KANJI


def search_kanji(kanji_char):
    """
    特定の漢字を検索
    
    Args:
        kanji_char (str): 検索する漢字
    
    Returns:
        tuple: (漢字データ, 学年) or (None, None)
    """
    for grade, kanji_list in GRADE_KANJI_MAP.items():
        for kanji_data in kanji_list:
            if kanji_data[0] == kanji_char:
                return kanji_data, grade
    return None, None


def get_kanji_stats():
    """
    漢字データの統計情報を取得
    
    Returns:
        dict: 統計情報
    """
    stats = {
        "total": len(ALL_JOYO_KANJI),
        "elementary": len(ELEMENTARY_KANJI),
        "junior_high": len(JUNIOR_HIGH_KANJI),
        "others": len(KANJI_OTHERS),
        "by_grade": {}
    }
    
    for grade, kanji_list in GRADE_KANJI_MAP.items():
        if grade <= 6:
            stats["by_grade"][f"grade_{grade}"] = len(kanji_list)
        elif grade <= 9:
            stats["by_grade"][f"junior_high_{grade-6}"] = len(kanji_list)
        else:
            stats["by_grade"]["others"] = len(kanji_list)
    
    return stats


if __name__ == "__main__":
    # 統計情報を表示
    stats = get_kanji_stats()
    print("常用漢字データベース統計:")
    print(f"総漢字数: {stats['total']:,}字")
    print(f"小学校漢字: {stats['elementary']:,}字")
    print(f"中学校漢字: {stats['junior_high']:,}字")
    print(f"その他: {stats['others']:,}字")
    print("\n学年別内訳:")
    for grade_key, count in stats['by_grade'].items():
        print(f"  {grade_key}: {count:,}字")
    
    # サンプル表示
    print("\n各学年のサンプル漢字:")
    for grade in range(1, 10):
        kanji_list = get_kanji_by_grade(grade)
        if kanji_list:
            sample = kanji_list[0]
            grade_name = f"小学{grade}年" if grade <= 6 else f"中学{grade-6}年"
            print(f"{grade_name}: {sample[0]} (音: {sample[1]}, 訓: {sample[2]})")