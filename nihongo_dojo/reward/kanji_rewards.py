"""
漢字学習タスク専用の改良版報酬関数
"""

import re
from typing import List, Dict, Any, Optional
import unicodedata


class KanjiRewardFunctions:
    """漢字学習タスク用の改良された報酬関数"""
    
    def __init__(self, reasoning_start="<reasoning>", reasoning_end="</reasoning>",
                 solution_start="<answer>", solution_end="</answer>", 
                 eos_token=""):
        self.reasoning_start = reasoning_start
        self.reasoning_end = reasoning_end
        self.solution_start = solution_start
        self.solution_end = solution_end
        self.eos_token = eos_token
        
        # 正規表現パターンを作成
        self._create_regex_pattern()
        
        # よくある間違いパターン
        self.COMMON_MISTAKES = {
            # 読み方の混同
            "紅": ["くれない", "べに", "こう"],  # 「くれない」を「与えない」と誤解
            "十": ["じゅう", "じっ", "じゅっ", "とお"],
            "反": ["はん", "たん", "へん"],
            "都": ["と", "つ"],
            
            # 同音異義語
            "留": ["と", "る", "りゅう"],
            "張": ["は", "ちょう"],
            "常": ["とこ", "じょう"],
        }
        
        # 部首や形が似ている漢字
        self.SIMILAR_KANJI = {
            "日": ["目", "白", "旧"],
            "人": ["入", "八"],
            "土": ["士", "工"],
            "我": ["找", "戒"],
            "川": ["州", "順"],
        }
    
    def _create_regex_pattern(self):
        """フォーマット確認用の正規表現パターンを作成"""
        solution_end_regex = r"</answer>[\s]{0,}"
        if self.eos_token:
            solution_end_regex += "(?:" + re.escape(self.eos_token) + ")?"
        
        self.match_format = re.compile(
            rf"{self.reasoning_end}.*?"
            rf"{self.solution_start}(.+?){solution_end_regex}"
            rf"[\s]{{0,}}$",
            flags=re.MULTILINE | re.DOTALL
        )
    
    def balanced_check_kanji_answer(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """バランスの取れた漢字答え確認（より詳細な部分点評価）"""
        # 新しいインターフェース対応
        if prompts is not None and completions is not None:
            # answerがフルソリューション形式の場合、実際の答えを抽出
            if answer and len(answer) > 0 and isinstance(answer[0], str) and '<answer>' in answer[0]:
                extracted_answers = []
                for ans in answer:
                    match = re.search(r'<answer>(.+?)</answer>', ans, re.DOTALL)
                    if match:
                        extracted_answers.append(match.group(1).strip())
                    else:
                        extracted_answers.append(ans)
                answer = extracted_answers
            
            # completionsから応答を抽出
            responses = []
            for completion in completions:
                if isinstance(completion, str):
                    responses.append(completion)
                elif isinstance(completion, list) and len(completion) > 0:
                    responses.append(completion[0].get("content", "") if isinstance(completion[0], dict) else str(completion[0]))
                else:
                    responses.append("")
        else:
            # 古いインターフェース
            responses = kwargs.get('completions', [])
            if not responses and 'responses' in kwargs:
                responses = kwargs['responses']
        
        # 答えがリストでない場合はリストに変換
        if not isinstance(answer, list):
            answer = [answer] * len(responses)
        elif len(answer) == 1 and len(responses) > 1:
            answer = answer * len(responses)
        
        extracted_responses = [
            guess.group(1)
            if (guess := self.match_format.search(r)) is not None else None
            for r in responses
        ]
        
        scores = []
        
        for guess, true_answer in zip(extracted_responses, answer):
            score = 0
            
            # フォーマットエラー
            if guess is None:
                scores.append(-3.0)  # より厳しいペナルティ
                continue
            
            # 答えをクリーンアップ
            guess = guess.strip()
            true_answer = str(true_answer).strip()
            
            # 漢字タスクの評価
            score = self._evaluate_kanji_answer(guess, true_answer)
            
            scores.append(score)
        
        # 抽出された回答をkwargsに追加（ログ記録用）
        kwargs['extracted_responses'] = extracted_responses
        
        return scores
    
    def _evaluate_kanji_answer(self, guess: str, answer: str) -> float:
        """漢字の答えを詳細評価"""
        # 完全一致
        if guess == answer:
            return 2.0  # 基本点を下げる
        
        # 正規化して比較（Unicode正規化）
        normalized_guess = unicodedata.normalize('NFKC', guess)
        normalized_answer = unicodedata.normalize('NFKC', answer)
        if normalized_guess == normalized_answer:
            return 1.8
        
        # 部分的に正しい場合の評価
        # 1. 読み方の部分一致（音読み・訓読み）
        if self._is_reading_partially_correct(guess, answer):
            return 0.8
        
        # 2. 似た形の漢字（部首が同じなど）
        if self._is_similar_kanji(guess, answer):
            return 0.3
        
        # 3. 音が似ている（同音異義語）
        if self._is_similar_sound(guess, answer):
            return 0.2
        
        # 4. 文字数が同じで一部が正しい
        if len(guess) == len(answer):
            common_chars = sum(1 for g, a in zip(guess, answer) if g == a)
            if common_chars > 0:
                return 0.5 * (common_chars / len(answer))
        
        # 5. 意味的に関連がある場合（例：「川」と「河」）
        if self._is_semantically_related(guess, answer):
            return 0.1
        
        # 完全に間違い
        return -1.5
    
    def _is_reading_partially_correct(self, guess: str, answer: str) -> bool:
        """読み方が部分的に正しいかチェック"""
        # ひらがな・カタカナの場合
        if (self._is_kana(guess) and self._is_kana(answer)):
            # 促音・拗音の違いを許容
            normalized_guess = guess.replace("っ", "つ").replace("ゃ", "や").replace("ゅ", "ゆ").replace("ょ", "よ")
            normalized_answer = answer.replace("っ", "つ").replace("ゃ", "や").replace("ゅ", "ゆ").replace("ょ", "よ")
            if normalized_guess == normalized_answer:
                return True
            
            # 濁音・半濁音の違い
            if self._remove_dakuten(guess) == self._remove_dakuten(answer):
                return True
            
            # 長音の違い（「こう」と「こー」など）
            if guess.replace("う", "ー") == answer or answer.replace("う", "ー") == guess:
                return True
        
        return False
    
    def _is_similar_kanji(self, guess: str, answer: str) -> bool:
        """形が似ている漢字かチェック"""
        # 似ている漢字のリストから確認
        for kanji, similar_list in self.SIMILAR_KANJI.items():
            if answer == kanji and guess in similar_list:
                return True
            if guess == kanji and answer in similar_list:
                return True
        
        # 部首が同じかチェック（簡易版）
        common_radicals = ["氵", "亻", "木", "火", "土", "金", "水", "日", "月", "⺾"]
        for radical in common_radicals:
            if radical in guess and radical in answer:
                return True
        
        return False
    
    def _is_similar_sound(self, guess: str, answer: str) -> bool:
        """音が似ているかチェック"""
        # よくある間違いパターンから確認
        for kanji, readings in self.COMMON_MISTAKES.items():
            if answer == kanji or guess == kanji:
                return guess in readings or answer in readings
        
        return False
    
    def _is_semantically_related(self, guess: str, answer: str) -> bool:
        """意味的に関連があるかチェック"""
        semantic_groups = [
            ["川", "河", "江"],
            ["山", "岳", "峰"],
            ["木", "樹", "林", "森"],
            ["日", "陽", "太陽"],
            ["月", "月光", "月夜"],
            ["火", "炎", "焔"],
            ["水", "氷", "湯"],
        ]
        
        for group in semantic_groups:
            if guess in group and answer in group:
                return True
        
        return False
    
    def _is_kana(self, text: str) -> bool:
        """ひらがな・カタカナかチェック"""
        return all(unicodedata.name(c, '').startswith(('HIRAGANA', 'KATAKANA')) or c in 'ー' for c in text)
    
    def _remove_dakuten(self, text: str) -> str:
        """濁音・半濁音を清音に変換"""
        dakuten_map = str.maketrans(
            'がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ',
            'かきくけこさしすせそたちつてとはひふへほはひふへほ'
        )
        return text.translate(dakuten_map)
    
    def enhanced_kanji_quality(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """強化された漢字品質評価（学習説明の質を重視）"""
        if prompts is not None and completions is not None:
            responses = completions
            questions = []
            for prompt in prompts:
                if isinstance(prompt, list) and len(prompt) > 0:
                    question = prompt[-1].get("content", "") if isinstance(prompt[-1], dict) else str(prompt[-1])
                else:
                    question = str(prompt)
                questions.append(question)
        else:
            responses = kwargs.get('completions', [])
            questions = [kwargs.get('question', '')]
        
        scores = []
        
        for i, response in enumerate(responses):
            if isinstance(response, str):
                text = response
            elif isinstance(response, list) and len(response) > 0:
                text = response[0].get("content", "") if isinstance(response[0], dict) else str(response[0])
            else:
                text = ""
            
            score = 0
            
            # reasoning部分を抽出
            reasoning_match = re.search(
                rf"{self.reasoning_start}(.*?){self.reasoning_end}", 
                text, re.DOTALL
            )
            
            if reasoning_match:
                reasoning = reasoning_match.group(1)
                
                # 漢字学習説明の質を詳細評価
                score += self._evaluate_kanji_explanation(reasoning)
                
                # 答えとの整合性チェック
                extracted_match = self.match_format.search(text)
                if extracted_match and i < len(answer):
                    extracted_answer = extracted_match.group(1).strip()
                    true_answer = answer[i] if isinstance(answer, list) else answer
                    
                    # フルソリューションから答えを抽出
                    if isinstance(true_answer, str) and '<answer>' in true_answer:
                        answer_match = re.search(r'<answer>(.+?)</answer>', true_answer, re.DOTALL)
                        if answer_match:
                            true_answer = answer_match.group(1).strip()
                    
                    # 説明と答えの整合性
                    score += self._evaluate_explanation_consistency(reasoning, extracted_answer, true_answer)
            else:
                score = -1.0  # reasoning部分がない場合の強いペナルティ
            
            scores.append(score)
        
        return scores
    
    def _evaluate_kanji_explanation(self, reasoning: str) -> float:
        """漢字学習説明の質を評価"""
        score = 0
        
        # 漢字学習に関するキーワード
        learning_keywords = [
            "年生", "習う", "学年", "小学", "中学",
            "音読み", "訓読み", "おんよみ", "くんよみ",
            "意味", "部首", "画数", "書き順"
        ]
        
        # 説明の要素
        explanation_elements = [
            "これは", "この漢字は", "という漢字",
            "読み方は", "と読みます", "という意味",
            "などです", "を表します"
        ]
        
        # キーワードの使用カウント
        keyword_count = sum(1 for keyword in learning_keywords if keyword in reasoning)
        element_count = sum(1 for element in explanation_elements if element in reasoning)
        
        # 学習キーワードの使用に応じて加点
        if keyword_count >= 3:
            score += 0.4
        elif keyword_count >= 2:
            score += 0.2
        elif keyword_count >= 1:
            score += 0.1
        
        # 説明要素の使用
        if element_count >= 2:
            score += 0.2
        elif element_count >= 1:
            score += 0.1
        
        # 説明の長さと質
        length = len(reasoning)
        if 30 < length < 150:
            score += 0.2
        elif 150 <= length < 250:
            score += 0.1
        elif length >= 250:
            score -= 0.1  # 冗長すぎる
        elif length <= 30:
            score -= 0.2  # 短すぎる
        
        # 英語での意味説明があるか（ボーナス）
        if re.search(r'[a-zA-Z]{3,}', reasoning):
            score += 0.1
        
        return min(score, 1.0)  # 最大1.0
    
    def _evaluate_explanation_consistency(self, reasoning: str, extracted: str, expected: str) -> float:
        """説明と答えの整合性を評価"""
        score = 0
        
        # 答えが正しい場合
        if extracted == expected:
            # 正しい学年が説明されているか
            grade_patterns = [
                r"小学(\d)年生", r"(\d)年生で習う", 
                r"中学(\d)年生", r"常用漢字"
            ]
            if any(re.search(pattern, reasoning) for pattern in grade_patterns):
                score += 0.2
            
            # 読み方の種類が正しく説明されているか
            if "音読み" in reasoning or "訓読み" in reasoning:
                score += 0.1
        else:
            # 答えが間違っている場合
            if extracted in reasoning:
                score -= 0.2  # 間違った答えを説明で正当化している
            
            # 部分的に正しい説明があるか
            if self._is_reading_partially_correct(extracted, expected):
                score += 0.1
        
        return score
    
    def strict_format_check(self, prompts=None, completions=None, completion_ids=None, **kwargs):
        """厳格なフォーマットチェック（ペナルティ強化版）"""
        if prompts is not None and completions is not None:
            responses = completions
        else:
            responses = kwargs.get('completions', [])
        
        scores = []
        
        for response in responses:
            score = 0
            if isinstance(response, str):
                text = response
            elif isinstance(response, list) and len(response) > 0:
                text = response[0].get("content", "") if isinstance(response[0], dict) else str(response[0])
            else:
                text = ""
            
            # 完全なフォーマットチェック
            has_reasoning_start = self.reasoning_start in text
            has_reasoning_end = self.reasoning_end in text
            has_solution_start = self.solution_start in text
            has_solution_end = self.solution_end in text
            
            # すべての要素が正しい順序で存在するか
            if has_reasoning_start and has_reasoning_end and has_solution_start and has_solution_end:
                # 順序の確認
                idx_rs = text.find(self.reasoning_start)
                idx_re = text.find(self.reasoning_end)
                idx_ss = text.find(self.solution_start)
                idx_se = text.find(self.solution_end)
                
                if idx_rs < idx_re < idx_ss < idx_se:
                    score = 0.5  # 正しいフォーマット
                else:
                    score = -1.0  # 順序が間違っている
            else:
                # 欠けている要素ごとにペナルティ
                missing_count = sum([
                    not has_reasoning_start,
                    not has_reasoning_end,
                    not has_solution_start,
                    not has_solution_end
                ])
                score = -0.5 * missing_count
            
            scores.append(score)
        
        return scores
    
    def check_grade_accuracy(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """学年の正確性を評価（漢字タスク特有）"""
        if prompts is not None and completions is not None:
            responses = completions
        else:
            responses = kwargs.get('completions', [])
        
        scores = []
        
        # 実際の学年データ（簡易版）
        grade_data = {
            1: ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "日", "月", "火", "水", "木", "金", "土"],
            2: ["国", "語", "算", "数", "理", "科", "社", "会", "音", "楽", "図", "工", "体", "育", "家", "庭"],
            3: ["医", "者", "学", "校", "先", "生", "友", "達", "兄", "弟", "姉", "妹", "父", "母", "祖", "先"],
            4: ["英", "語", "歴", "史", "地", "理", "政", "治", "経", "済", "文", "化", "芸", "術", "技", "術"],
            5: ["情", "報", "環", "境", "国", "際", "平", "和", "民", "主", "自", "由", "権", "利", "義", "務"],
            6: ["憲", "法", "裁", "判", "警", "察", "防", "衛", "外", "交", "貿", "易", "産", "業", "商", "業"],
        }
        
        for response in responses:
            if isinstance(response, str):
                text = response
            elif isinstance(response, list) and len(response) > 0:
                text = response[0].get("content", "") if isinstance(response[0], dict) else str(response[0])
            else:
                text = ""
            
            score = 0
            
            # 学年の記載を探す
            grade_match = re.search(r'小学(\d)年生', text)
            if grade_match:
                mentioned_grade = int(grade_match.group(1))
                
                # 答えの漢字を抽出
                extracted_match = self.match_format.search(text)
                if extracted_match:
                    kanji = extracted_match.group(1).strip()
                    
                    # 正しい学年か確認（簡易チェック）
                    correct_grade = None
                    for grade, kanji_list in grade_data.items():
                        if any(k in kanji for k in kanji_list):
                            correct_grade = grade
                            break
                    
                    if correct_grade and mentioned_grade == correct_grade:
                        score += 0.3
                    elif correct_grade and abs(mentioned_grade - correct_grade) == 1:
                        score += 0.1  # 1学年違い
                    else:
                        score -= 0.1  # 大きく違う
            
            scores.append(score)
        
        return scores
    
    def get_balanced_reward_functions(self):
        """バランスの取れた報酬関数セットを返す"""
        return [
            self.strict_format_check,           # フォーマットチェック（厳格版）
            self.balanced_check_kanji_answer,   # 漢字答えチェック（バランス版）
            self.enhanced_kanji_quality,        # 品質チェック（強化版）
            self.check_grade_accuracy,          # 学年正確性チェック
        ]