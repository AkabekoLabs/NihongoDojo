"""
敬語変換タスク専用の改良版報酬関数
"""

import re
from typing import List, Dict, Any, Optional


class KeigoRewardFunctions:
    """敬語タスク用の改良された報酬関数"""
    
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
        
        # 敬語のペア定義（基本形: [尊敬語, 謙譲語]）
        self.KEIGO_PAIRS = {
            "行く": ["いらっしゃる/おいでになる", "参る/伺う"],
            "来る": ["いらっしゃる/おいでになる/お見えになる", "参る/伺う"],
            "いる": ["いらっしゃる/おいでになる", "おる"],
            "する": ["なさる/される", "いたす"],
            "言う": ["おっしゃる", "申す/申し上げる"],
            "見る": ["ご覧になる", "拝見する"],
            "聞く": ["お聞きになる", "伺う/拝聴する"],
            "食べる": ["召し上がる", "いただく"],
            "飲む": ["召し上がる", "いただく"],
            "もらう": ["お受け取りになる", "いただく/頂戴する"],
            "あげる": ["くださる", "差し上げる"],
            "知る": ["ご存知である", "存じる/存じ上げる"],
            "思う": ["お思いになる", "存じる"],
            "会う": ["お会いになる", "お目にかかる"],
            "読む": ["お読みになる", "拝読する"],
            "書く": ["お書きになる", "書かせていただく"],
            "待つ": ["お待ちになる", "お待ちする"],
            "寝る": ["お休みになる", "休ませていただく"],
            "死ぬ": ["お亡くなりになる", "(使用を避ける)"],
        }
        
        # 丁寧語のバリエーション
        self.POLITE_VARIATIONS = {
            "おる": "おります",
            "いたす": "いたします",
            "申す": "申します",
            "参る": "参ります",
            "伺う": "伺います",
            "いただく": "いただきます",
            "差し上げる": "差し上げます",
            "存じる": "存じます",
            "拝見する": "拝見します",
            "拝読する": "拝読します",
            "拝聴する": "拝聴します",
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
    
    def balanced_check_keigo(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """バランスの取れた敬語チェック（丁寧語バリエーション対応）"""
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
                scores.append(-3.0)  # 厳しいペナルティ
                continue
            
            # 答えをクリーンアップ
            guess = guess.strip()
            true_answer = str(true_answer).strip()
            
            # 敬語の評価
            score = self._evaluate_keigo_answer(guess, true_answer)
            
            scores.append(score)
        
        # 抽出された回答をkwargsに追加（ログ記録用）
        kwargs['extracted_responses'] = extracted_responses
        
        return scores
    
    def _evaluate_keigo_answer(self, guess: str, answer: str) -> float:
        """敬語の答えを詳細評価"""
        # 完全一致
        if guess == answer:
            return 3.0
        
        # 丁寧語のバリエーションチェック
        if self._is_polite_variation(guess, answer):
            return 2.5  # ほぼ正解として扱う
        
        # 同じ敬語カテゴリー内の別表現
        if self._is_same_keigo_category(guess, answer):
            return 2.0  # 別の正しい表現
        
        # 敬語の種類の混同（尊敬語↔謙譲語）
        if self._is_keigo_confusion(guess, answer):
            return -1.0  # カテゴリー混同は重いペナルティ
        
        # 部分的に正しい場合
        if self._is_partially_correct(guess, answer):
            return 0.5
        
        # 完全に間違い
        return -1.5
    
    def _is_polite_variation(self, guess: str, answer: str) -> bool:
        """丁寧語のバリエーションかチェック"""
        # おる → おります のパターン
        for plain, polite in self.POLITE_VARIATIONS.items():
            if (guess == polite and answer == plain) or (guess == plain and answer == polite):
                return True
        
        # です・ます調の違い
        if guess.replace("です", "") == answer.replace("です", ""):
            return True
        if guess.replace("ます", "") == answer.replace("ます", ""):
            return True
        
        return False
    
    def _is_same_keigo_category(self, guess: str, answer: str) -> bool:
        """同じ敬語カテゴリー内の別表現かチェック"""
        for base_verb, [sonkeigo, kenjogo] in self.KEIGO_PAIRS.items():
            # 尊敬語の別表現
            sonkeigo_options = sonkeigo.split("/")
            if guess in sonkeigo_options and answer in sonkeigo_options:
                return True
            
            # 謙譲語の別表現
            kenjogo_options = kenjogo.split("/")
            if guess in kenjogo_options and answer in kenjogo_options:
                return True
        
        return False
    
    def _is_keigo_confusion(self, guess: str, answer: str) -> bool:
        """敬語の種類の混同かチェック"""
        for base_verb, [sonkeigo, kenjogo] in self.KEIGO_PAIRS.items():
            sonkeigo_options = sonkeigo.split("/")
            kenjogo_options = kenjogo.split("/")
            
            # 尊敬語を期待して謙譲語が来た
            if answer in sonkeigo_options and guess in kenjogo_options:
                return True
            
            # 謙譲語を期待して尊敬語が来た
            if answer in kenjogo_options and guess in sonkeigo_options:
                return True
        
        return False
    
    def _is_partially_correct(self, guess: str, answer: str) -> bool:
        """部分的に正しいかチェック"""
        # お/ご + 動詞 + する/になる パターン
        if "お" in guess and "お" in answer:
            # お待ちする vs お待ちになる のような場合
            guess_stem = guess.replace("する", "").replace("になる", "")
            answer_stem = answer.replace("する", "").replace("になる", "")
            if guess_stem == answer_stem:
                return True
        
        # 語幹が同じ場合
        common_stems = ["いらっしゃ", "おっしゃ", "なさ", "くださ", "召し上が"]
        for stem in common_stems:
            if stem in guess and stem in answer:
                return True
        
        return False
    
    def enhanced_keigo_quality(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """強化された敬語品質評価（文法説明の質を重視）"""
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
                question = questions[i] if i < len(questions) else ""
                
                # 敬語説明の質を評価
                score += self._evaluate_keigo_explanation(reasoning, question)
                
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
    
    def _evaluate_keigo_explanation(self, reasoning: str, question: str) -> float:
        """敬語説明の質を評価"""
        score = 0
        
        # 敬語に関するキーワード
        keigo_keywords = [
            "尊敬語", "謙譲語", "丁寧語", "敬語",
            "相手", "自分", "動作", "へりくだ", "敬意"
        ]
        
        # 変換タイプの特定
        if "尊敬語" in question:
            expected_type = "尊敬語"
        elif "謙譲語" in question:
            expected_type = "謙譲語"
        else:
            expected_type = None
        
        # キーワードの使用カウント
        keyword_count = sum(1 for keyword in keigo_keywords if keyword in reasoning)
        
        # キーワードの使用に応じて加点
        if keyword_count >= 3:
            score += 0.4
        elif keyword_count >= 2:
            score += 0.2
        elif keyword_count >= 1:
            score += 0.1
        
        # 正しい敬語タイプが説明されているか
        if expected_type and expected_type in reasoning:
            score += 0.2
        
        # 説明の構造
        if "ので" in reasoning or "ため" in reasoning or "から" in reasoning:
            score += 0.1  # 理由説明がある
        
        # 説明の長さ
        length = len(reasoning)
        if 30 < length < 150:
            score += 0.2
        elif 150 <= length < 250:
            score += 0.1
        elif length >= 250:
            score -= 0.1  # 冗長すぎる
        elif length <= 30:
            score -= 0.2  # 短すぎる
        
        return min(score, 1.0)  # 最大1.0
    
    def _evaluate_explanation_consistency(self, reasoning: str, extracted: str, expected: str) -> float:
        """説明と答えの整合性を評価"""
        score = 0
        
        # 答えが正しい場合
        if extracted == expected or self._is_polite_variation(extracted, expected):
            # 正しい動詞形が説明されているか
            if extracted in reasoning:
                score += 0.2
            
            # 敬語の種類が正しく説明されているか
            if "尊敬語" in reasoning or "謙譲語" in reasoning:
                score += 0.1
        else:
            # 答えが間違っている場合
            if self._is_keigo_confusion(extracted, expected):
                # カテゴリー混同の説明があるか
                if "尊敬語" in reasoning and "謙譲語" in reasoning:
                    score -= 0.3  # 混同している
            
            if extracted in reasoning:
                score -= 0.2  # 間違った答えを説明で正当化している
        
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
    
    def check_keigo_type_accuracy(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """敬語タイプの正確性を評価（尊敬語/謙譲語の区別）"""
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
            questions = [kwargs.get('question', '')] * len(responses)
        
        scores = []
        
        # 答えの処理
        if answer and isinstance(answer, list):
            if len(answer) > 0 and isinstance(answer[0], str) and '<answer>' in answer[0]:
                extracted_answers = []
                for ans in answer:
                    match = re.search(r'<answer>(.+?)</answer>', ans, re.DOTALL)
                    if match:
                        extracted_answers.append(match.group(1).strip())
                    else:
                        extracted_answers.append(ans)
                answer = extracted_answers
        
        if not isinstance(answer, list):
            answer = [answer] * len(responses)
        
        for i, response in enumerate(responses):
            if isinstance(response, str):
                text = response
            elif isinstance(response, list) and len(response) > 0:
                text = response[0].get("content", "") if isinstance(response[0], dict) else str(response[0])
            else:
                text = ""
            
            score = 0
            question = questions[i] if i < len(questions) else ""
            
            # 答えを抽出
            extracted_match = self.match_format.search(text)
            if extracted_match and i < len(answer):
                extracted_answer = extracted_match.group(1).strip()
                true_answer = answer[i]
                
                # 要求された敬語タイプを特定
                if "尊敬語" in question:
                    required_type = "sonkeigo"
                elif "謙譲語" in question:
                    required_type = "kenjogo"
                else:
                    required_type = None
                
                if required_type:
                    # 正しいタイプの敬語を使っているか確認
                    is_correct_type = self._check_keigo_type(extracted_answer, required_type)
                    
                    if is_correct_type:
                        score += 0.3
                    else:
                        # タイプが間違っている場合
                        if self._is_keigo_confusion(extracted_answer, true_answer):
                            score -= 0.5  # カテゴリー混同
                        else:
                            score -= 0.2  # その他の間違い
            
            scores.append(score)
        
        return scores
    
    def _check_keigo_type(self, word: str, required_type: str) -> bool:
        """単語が要求された敬語タイプか確認"""
        for base_verb, [sonkeigo, kenjogo] in self.KEIGO_PAIRS.items():
            if required_type == "sonkeigo":
                if word in sonkeigo.split("/"):
                    return True
            elif required_type == "kenjogo":
                if word in kenjogo.split("/"):
                    return True
        
        # お/ご + 動詞 + になる/する パターン
        if required_type == "sonkeigo" and "になる" in word:
            return True
        if required_type == "kenjogo" and word.endswith("する") and word.startswith(("お", "ご")):
            return True
        
        return False
    
    def get_balanced_reward_functions(self):
        """バランスの取れた報酬関数セットを返す"""
        return [
            self.strict_format_check,        # フォーマットチェック（厳格版）
            self.balanced_check_keigo,       # 敬語チェック（バランス版）
            self.enhanced_keigo_quality,     # 品質チェック（強化版）
            self.check_keigo_type_accuracy,  # 敬語タイプ正確性チェック
        ]