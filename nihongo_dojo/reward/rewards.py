"""
日本語タスク用の報酬関数
"""

import re
from collections import defaultdict


class JapaneseTaskRewardFunctions:
    """日本語タスク用の報酬関数を提供するクラス"""
    
    def __init__(self, reasoning_start="<reasoning>", reasoning_end="</reasoning>",
                 solution_start="<answer>", solution_end="</answer>", 
                 eos_token="", accuracy_stats=None):
        self.reasoning_start = reasoning_start
        self.reasoning_end = reasoning_end
        self.solution_start = solution_start
        self.solution_end = solution_end
        self.eos_token = eos_token
        
        # 統計情報を保存
        self.accuracy_stats = accuracy_stats or defaultdict(list)
        
        # 正規表現パターンを作成
        self._create_regex_pattern()
    
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
    
    def match_format_exactly(self, prompts=None, completions=None, completion_ids=None, **kwargs):
        """フォーマットの完全一致を確認（統計収集付き）"""
        # 新しいインターフェース対応
        if prompts is not None and completions is not None:
            responses = completions
        else:
            # 古いインターフェース（後方互換性）
            responses = kwargs.get('completions', [])
        
        scores = []
        format_success = 0
        
        for response in responses:
            score = 0
            # 新しいインターフェースの場合は文字列、古い場合は辞書
            if isinstance(response, str):
                text = response
            elif isinstance(response, list) and len(response) > 0:
                text = response[0].get("content", "") if isinstance(response[0], dict) else str(response[0])
            else:
                text = ""
            
            # フォーマットが正確に見つかった場合
            if self.match_format.search(text) is not None:
                score += 1.0
                format_success += 1
                self.accuracy_stats['correct_format'].append(1)
            else:
                score = -1.0  # フォーマットエラーのペナルティ
                self.accuracy_stats['correct_format'].append(0)
            
            scores.append(score)
        
        if len(scores) > 0:
            format_rate = format_success / len(scores) * 100
            print(f"📋 フォーマット正答率: {format_rate:.1f}%")
        
        return scores
    
    def match_format_approximately(self, prompts=None, completions=None, completion_ids=None, **kwargs):
        """フォーマットの部分一致を確認"""
        # 新しいインターフェース対応
        if prompts is not None and completions is not None:
            responses = completions
        else:
            # 古いインターフェース（後方互換性）
            responses = kwargs.get('completions', [])
        
        scores = []
        
        for response in responses:
            score = 0
            # 新しいインターフェースの場合は文字列、古い場合は辞書
            if isinstance(response, str):
                text = response
            elif isinstance(response, list) and len(response) > 0:
                text = response[0].get("content", "") if isinstance(response[0], dict) else str(response[0])
            else:
                text = ""
            
            # キーワードをカウント
            score += 0.25 if text.count(self.reasoning_end) == 1 else -0.5
            score += 0.25 if text.count(self.solution_start) == 1 else -0.5
            score += 0.25 if text.count(self.solution_end) == 1 else -0.5
            
            scores.append(score)
        
        return scores
    
    def check_answer(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """答えの確認（より厳格な評価、統計収集付き）"""
        # 新しいインターフェース対応
        if prompts is not None and completions is not None:
            # answerがフルソリューション形式の場合、実際の答えを抽出
            if answer and len(answer) > 0 and isinstance(answer[0], str) and '<answer>' in answer[0]:
                # フルソリューションから実際の答えを抽出
                extracted_answers = []
                for ans in answer:
                    match = re.search(r'<answer>(.+?)</answer>', ans, re.DOTALL)
                    if match:
                        extracted_answers.append(match.group(1).strip())
                    else:
                        extracted_answers.append(ans)  # フォールバック
                answer = extracted_answers
            
            # promptsからquestionと答えを抽出
            if prompts and len(prompts) > 0 and not answer:
                # 最後のメッセージから質問を取得
                question = prompts[0] if isinstance(prompts[0], str) else prompts[0][-1].get("content", "")
                # 答えを抽出 - "正解:" の後の部分を探す
                import re
                answer_match = re.search(r'正解[：:]\s*([^\n]+)', question)
                if answer_match:
                    answer = [answer_match.group(1).strip()]
                elif not answer:
                    # 答えが見つからない場合は空リスト
                    answer = [""] * len(completions)
            
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
            # 古いインターフェース（後方互換性）
            question = kwargs.get('question', '')
            answer = kwargs.get('answer', [])
            responses = kwargs.get('responses', [])
            if not responses and 'completions' in kwargs:
                completions = kwargs['completions']
                responses = [completion[0]["content"] for completion in completions]
        
        # 答えがリストでない場合はリストに変換
        if not isinstance(answer, list):
            answer = [answer] * len(responses)
        elif len(answer) == 1 and len(responses) > 1:
            # 答えが1つしかない場合は、全ての応答に対して同じ答えを使用
            answer = answer * len(responses)
        
        extracted_responses = [
            guess.group(1)
            if (guess := self.match_format.search(r)) is not None else None
            for r in responses
        ]
        
        scores = []
        batch_stats = {'correct': 0, 'partial': 0, 'wrong': 0, 'no_answer': 0}
        
        for guess, true_answer in zip(extracted_responses, answer):
            score = 0
            if guess is None:
                scores.append(-2.0)
                batch_stats['no_answer'] += 1
                self.accuracy_stats['no_answer'].append(1)
                continue
            
            # 答えをクリーンアップ
            guess = guess.strip()
            true_answer = str(true_answer).strip()
            
            # 完全一致
            if guess == true_answer:
                score += 3.0
                batch_stats['correct'] += 1
                self.accuracy_stats['correct_answer'].append(1)
            # スペースなしで一致
            elif guess.replace(" ", "") == true_answer.replace(" ", ""):
                score += 2.5
                batch_stats['correct'] += 1
                self.accuracy_stats['correct_answer'].append(1)
            # ひらがな/カタカナの違いは許容（ただし減点）
            elif guess.replace("　", "").replace("、", "") == true_answer.replace("　", "").replace("、", ""):
                score += 2.0
                batch_stats['partial'] += 1
                self.accuracy_stats['partial_answer'].append(1)
            else:
                # 部分一致の評価をより詳細に
                if len(true_answer) == 1 and len(guess) == 1:
                    # 単一文字の場合（漢字一文字など）
                    score = -1.5
                elif true_answer in guess or guess in true_answer:
                    # 部分一致
                    match_ratio = min(len(guess), len(true_answer)) / max(len(guess), len(true_answer))
                    score += 1.0 * match_ratio
                    batch_stats['partial'] += 1
                    self.accuracy_stats['partial_answer'].append(1)
                else:
                    score = -1.5
                    batch_stats['wrong'] += 1
                    self.accuracy_stats['wrong_answer'].append(1)
            
            scores.append(score)
        
        # バッチ統計を表示
        if len(scores) > 0:
            accuracy = batch_stats['correct'] / len(scores) * 100
            print(f"📊 バッチ統計 - 正解率: {accuracy:.1f}% | 正解: {batch_stats['correct']} | " +
                  f"部分正解: {batch_stats['partial']} | 不正解: {batch_stats['wrong']} | 無回答: {batch_stats['no_answer']}")
        
        # 抽出された回答をkwargsに追加（ログ記録用）
        kwargs['extracted_responses'] = extracted_responses
        
        return scores
    
    def check_reasoning_quality(self, prompts=None, completions=None, completion_ids=None, **kwargs):
        """思考過程の質を評価"""
        # 新しいインターフェース対応
        if prompts is not None and completions is not None:
            responses = completions
        else:
            # 古いインターフェース（後方互換性）
            responses = kwargs.get('completions', [])
        
        scores = []
        
        for response in responses:
            # 新しいインターフェースの場合は文字列、古い場合は辞書
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
                
                # 漢字学習に関連するキーワードをチェック
                keywords = ["年生", "習う", "意味", "読み", "書き", "漢字", "音読み", "訓読み"]
                keyword_count = sum(1 for keyword in keywords if keyword in reasoning)
                
                if keyword_count >= 3:
                    score += 0.5  # 複数のキーワード
                elif keyword_count >= 1:
                    score += 0.2  # 少なくとも1つのキーワード
                
                # 説明の長さが適切か
                reasoning_length = len(reasoning)
                if 20 < reasoning_length < 100:
                    score += 0.3
                elif 100 <= reasoning_length < 200:
                    score += 0.1
                elif reasoning_length >= 200:
                    score -= 0.2  # 長すぎる説明はペナルティ
                
                # 英語の意味が含まれているか
                if re.search(r'[a-zA-Z]+', reasoning):
                    score += 0.1  # 英語での意味説明はボーナス
            else:
                score = -0.5  # reasoning部分がない場合のペナルティ
            
            scores.append(score)
        
        return scores
    
    def check_word_order_quality(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """語順タスクの品質を評価"""
        # 新しいインターフェース対応
        if prompts is not None and completions is not None:
            responses = completions
            questions = []
            for prompt in prompts:
                if isinstance(prompt, list) and len(prompt) > 0:
                    # メッセージリストから最後のユーザーメッセージを取得
                    question = prompt[-1].get("content", "") if isinstance(prompt[-1], dict) else str(prompt[-1])
                else:
                    question = str(prompt)
                questions.append(question)
        else:
            # 古いインターフェース（後方互換性）
            responses = kwargs.get('completions', [])
            questions = [kwargs.get('question', '')]
        
        scores = []
        
        for i, response in enumerate(responses):
            # 新しいインターフェースの場合は文字列、古い場合は辞書
            if isinstance(response, str):
                text = response
            elif isinstance(response, list) and len(response) > 0:
                text = response[0].get("content", "") if isinstance(response[0], dict) else str(response[0])
            else:
                text = ""
            
            score = 0
            
            # 語順に関する評価
            if i < len(questions):
                question = questions[i]
                
                # reasoning部分を抽出して語順の説明品質を評価
                reasoning_match = re.search(
                    rf"{self.reasoning_start}(.*?){self.reasoning_end}", 
                    text, re.DOTALL
                )
                
                if reasoning_match:
                    reasoning = reasoning_match.group(1)
                    
                    # 語順に関するキーワードをチェック
                    order_keywords = ["語順", "順番", "並び替え", "助詞", "主語", "述語", "文法", "正しい順序"]
                    keyword_count = sum(1 for keyword in order_keywords if keyword in reasoning)
                    
                    if keyword_count >= 3:
                        score += 0.5  # 複数のキーワード
                    elif keyword_count >= 1:
                        score += 0.2  # 少なくとも1つのキーワード
                    
                    # 説明の長さが適切か
                    reasoning_length = len(reasoning)
                    if 20 < reasoning_length < 150:
                        score += 0.3
                    elif 150 <= reasoning_length < 300:
                        score += 0.1
                
                # 抽出された回答を取得
                extracted_match = self.match_format.search(text)
                if extracted_match:
                    extracted_answer = extracted_match.group(1).strip()
                    
                    # 期待される回答を取得
                    expected_answer = answer[i] if answer and i < len(answer) else ""
                    if isinstance(expected_answer, str) and self.solution_start in expected_answer:
                        expected_match = self.match_format.search(expected_answer)
                        if expected_match:
                            expected_answer = expected_match.group(1).strip()
                    
                    # 語順の詳細評価
                    if extracted_answer and expected_answer:
                        score += self._evaluate_word_order_quality(question, extracted_answer, expected_answer)
            
            scores.append(score)
        
        return scores
    
    def _evaluate_word_order_quality(self, question, extracted, expected):
        """語順の詳細評価"""
        if not extracted or not expected:
            return 0
        
        bonus = 0
        
        # 助詞の正確性
        particles = ['は', 'が', 'を', 'に', 'で', 'と', 'から', 'まで', 'より', 'も', 'へ']
        for particle in particles:
            if particle in expected:
                expected_idx = expected.index(particle)
                if particle in extracted:
                    extracted_idx = extracted.index(particle)
                    # 助詞の相対位置の正確性
                    relative_pos_expected = expected_idx / len(expected)
                    relative_pos_extracted = extracted_idx / len(extracted)
                    if abs(relative_pos_expected - relative_pos_extracted) < 0.1:
                        bonus += 0.1
        
        # 主語の位置（日本語では通常文頭）
        subject_markers = ['私は', '彼は', '彼女は', 'これは', 'それは']
        for marker in subject_markers:
            if marker in expected and marker in extracted:
                expected_pos = expected.index(marker) / len(expected)
                extracted_pos = extracted.index(marker) / len(extracted)
                if expected_pos < 0.3 and extracted_pos < 0.3:
                    bonus += 0.2
        
        # 動詞の位置（日本語では通常文末）
        verb_endings = ['ます', 'です', 'である', 'だ', 'ました', 'でした', 'でしょう']
        for ending in verb_endings:
            if expected.endswith(ending) and extracted.endswith(ending):
                bonus += 0.3
                break
        
        # 語順の一般的な正確性
        expected_words = expected.split()
        extracted_words = extracted.split()
        
        if len(expected_words) == len(extracted_words):
            # 位置が正しい単語の割合
            correct_positions = sum(1 for i, (exp, ext) in enumerate(zip(expected_words, extracted_words)) if exp == ext)
            position_accuracy = correct_positions / len(expected_words)
            bonus += position_accuracy * 0.5
        
        return min(bonus, 1.0)  # 最大1.0のボーナス
    
    def check_particle_quality(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """助詞穴埋めタスクの品質を評価"""
        # 新しいインターフェース対応
        if prompts is not None and completions is not None:
            responses = completions
            questions = []
            for prompt in prompts:
                if isinstance(prompt, list) and len(prompt) > 0:
                    # メッセージリストから最後のユーザーメッセージを取得
                    question = prompt[-1].get("content", "") if isinstance(prompt[-1], dict) else str(prompt[-1])
                else:
                    question = str(prompt)
                questions.append(question)
        else:
            # 古いインターフェース（後方互換性）
            responses = kwargs.get('completions', [])
            questions = [kwargs.get('question', '')]
        
        scores = []
        
        # 一般的な助詞のリスト
        COMMON_PARTICLES = [
            "が", "を", "に", "で", "へ", "と", "の", "は", "も", "から", "まで", "より",
            "や", "など", "ので", "のに", "ても", "でも", "ては", "には", "では", "へは"
        ]
        
        for i, response in enumerate(responses):
            # 新しいインターフェースの場合は文字列、古い場合は辞書
            if isinstance(response, str):
                text = response
            elif isinstance(response, list) and len(response) > 0:
                text = response[0].get("content", "") if isinstance(response[0], dict) else str(response[0])
            else:
                text = ""
            
            score = 0
            
            # reasoning部分を抽出して助詞の説明品質を評価
            reasoning_match = re.search(
                rf"{self.reasoning_start}(.*?){self.reasoning_end}", 
                text, re.DOTALL
            )
            
            if reasoning_match:
                reasoning = reasoning_match.group(1)
                
                # 文法用語の使用をチェック
                grammar_terms = ["主語", "目的語", "対象", "場所", "方向", "手段", "理由", "時間", "動作", "助詞"]
                term_count = sum(1 for term in grammar_terms if term in reasoning)
                
                if term_count >= 2:
                    score += 0.5  # 複数の文法用語
                elif term_count >= 1:
                    score += 0.2  # 少なくとも1つの文法用語
                
                # 説明の長さが適切か
                reasoning_length = len(reasoning)
                if 20 < reasoning_length < 150:
                    score += 0.3
                elif 150 <= reasoning_length < 250:
                    score += 0.1
            
            # 抽出された回答を取得
            extracted_match = self.match_format.search(text)
            if extracted_match:
                extracted_answer = extracted_match.group(1).strip()
                
                # 助詞として妥当かチェック
                if extracted_answer in COMMON_PARTICLES:
                    score += 0.5  # 一般的な助詞なら加点
                elif len(extracted_answer) <= 3:  # 短い文字列なら助詞の可能性
                    score += 0.2
            
            scores.append(score)
        
        return scores
    
    def check_counter_quality(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """助数詞タスクの品質を評価"""
        # 新しいインターフェース対応
        if prompts is not None and completions is not None:
            responses = completions
            questions = []
            for prompt in prompts:
                if isinstance(prompt, list) and len(prompt) > 0:
                    # メッセージリストから最後のユーザーメッセージを取得
                    question = prompt[-1].get("content", "") if isinstance(prompt[-1], dict) else str(prompt[-1])
                else:
                    question = str(prompt)
                questions.append(question)
        else:
            # 古いインターフェース（後方互換性）
            responses = kwargs.get('completions', [])
            questions = [kwargs.get('question', '')]
        
        scores = []
        
        # 一般的な助数詞のパターン
        COMMON_COUNTERS = [
            "つ", "個", "本", "枚", "台", "人", "匹", "頭", "羽", "冊", "回", 
            "度", "番", "足", "着", "杯", "円", "歳", "時", "分", "秒", "日",
            "月", "年", "週間", "ヶ月", "階", "軒", "通", "件", "名", "機"
        ]
        
        for i, response in enumerate(responses):
            # 新しいインターフェースの場合は文字列、古い場合は辞書
            if isinstance(response, str):
                text = response
            elif isinstance(response, list) and len(response) > 0:
                text = response[0].get("content", "") if isinstance(response[0], dict) else str(response[0])
            else:
                text = ""
            
            score = 0
            
            # reasoning部分を抽出して助数詞の説明品質を評価
            reasoning_match = re.search(
                rf"{self.reasoning_start}(.*?){self.reasoning_end}", 
                text, re.DOTALL
            )
            
            if reasoning_match:
                reasoning = reasoning_match.group(1)
                
                # 助数詞に関するキーワードをチェック
                counter_keywords = ["助数詞", "数える", "カウント", "単位", "数字", "数量", "個数", "物の形", "分類"]
                keyword_count = sum(1 for keyword in counter_keywords if keyword in reasoning)
                
                if keyword_count >= 2:
                    score += 0.5  # 複数のキーワード
                elif keyword_count >= 1:
                    score += 0.2  # 少なくとも1つのキーワード
                
                # 音変化の説明があるか
                sound_change_keywords = ["音変化", "読み方", "発音", "いち", "に", "さん", "よん", "ご", "ろく", "なな", "はち", "きゅう", "じゅう"]
                if any(keyword in reasoning for keyword in sound_change_keywords):
                    score += 0.3
                
                # 説明の長さが適切か
                reasoning_length = len(reasoning)
                if 30 < reasoning_length < 200:
                    score += 0.3
                elif 200 <= reasoning_length < 300:
                    score += 0.1
            
            # 抽出された回答を取得
            extracted_match = self.match_format.search(text)
            if extracted_match:
                extracted_answer = extracted_match.group(1).strip()
                
                # 助数詞として妥当かチェック
                if any(counter in extracted_answer for counter in COMMON_COUNTERS):
                    score += 0.5  # 一般的な助数詞を含む
                # 数字＋助数詞の形式かチェック
                elif re.match(r'^[0-9０-９一二三四五六七八九十百千万億]+[ぁ-んァ-ン々]+$', extracted_answer):
                    score += 0.4
                elif len(extracted_answer) <= 10:  # 短い文字列なら助数詞の可能性
                    score += 0.2
            
            scores.append(score)
        
        return scores
    
    def check_keigo_quality(self, prompts=None, completions=None, completion_ids=None, answer=None, **kwargs):
        """敬語変換タスクの品質を評価"""
        # 新しいインターフェース対応
        if prompts is not None and completions is not None:
            responses = completions
            questions = []
            for prompt in prompts:
                if isinstance(prompt, list) and len(prompt) > 0:
                    # メッセージリストから最後のユーザーメッセージを取得
                    question = prompt[-1].get("content", "") if isinstance(prompt[-1], dict) else str(prompt[-1])
                else:
                    question = str(prompt)
                questions.append(question)
        else:
            # 古いインターフェース（後方互換性）
            responses = kwargs.get('completions', [])
            questions = [kwargs.get('question', '')]
        
        scores = []
        
        # 敬語のマーカー
        KEIGO_MARKERS = {
            "尊敬語": ["れる", "られる", "いらっしゃる", "おっしゃる", "召し上がる", "お/ご～になる", "～れます", "～られます"],
            "謙譲語": ["いたす", "申す", "伺う", "拝見", "お/ご～する", "させていただく", "いたします", "申し上げる"],
            "丁寧語": ["です", "ます", "ございます", "でございます"]
        }
        
        for i, response in enumerate(responses):
            # 新しいインターフェースの場合は文字列、古い場合は辞書
            if isinstance(response, str):
                text = response
            elif isinstance(response, list) and len(response) > 0:
                text = response[0].get("content", "") if isinstance(response[0], dict) else str(response[0])
            else:
                text = ""
            
            score = 0
            
            # reasoning部分を抽出して敬語の説明品質を評価
            reasoning_match = re.search(
                rf"{self.reasoning_start}(.*?){self.reasoning_end}", 
                text, re.DOTALL
            )
            
            if reasoning_match:
                reasoning = reasoning_match.group(1)
                
                # 敬語の種類に関するキーワードをチェック
                keigo_keywords = ["敬語", "尊敬語", "謙譲語", "丁寧語", "美化語", "敬意", "相手", "立場", "上下関係"]
                keyword_count = sum(1 for keyword in keigo_keywords if keyword in reasoning)
                
                if keyword_count >= 3:
                    score += 0.5  # 複数のキーワード
                elif keyword_count >= 1:
                    score += 0.2  # 少なくとも1つのキーワード
                
                # 具体的な敬語形式の説明があるか
                if any(marker in reasoning for markers in KEIGO_MARKERS.values() for marker in markers):
                    score += 0.3
                
                # 説明の長さが適切か
                reasoning_length = len(reasoning)
                if 30 < reasoning_length < 200:
                    score += 0.3
                elif 200 <= reasoning_length < 300:
                    score += 0.1
            
            # 抽出された回答を取得
            extracted_match = self.match_format.search(text)
            if extracted_match:
                extracted_answer = extracted_match.group(1).strip()
                
                # 敬語マーカーを含むかチェック
                keigo_score = 0
                for keigo_type, markers in KEIGO_MARKERS.items():
                    if any(marker in extracted_answer for marker in markers):
                        keigo_score += 0.3
                        break
                
                # 文末が敬語らしいかチェック
                if extracted_answer.endswith(("ます", "です", "ました", "でした", "ございます", "いたします")):
                    keigo_score += 0.2
                
                score += min(keigo_score, 0.5)  # 最大0.5点
            
            scores.append(score)
        
        return scores
    
    def get_all_reward_functions(self):
        """すべての報酬関数をリストで返す"""
        return [
            self.match_format_exactly,
            self.match_format_approximately,
            self.check_answer,
            self.check_reasoning_quality,
            self.check_word_order_quality,
            self.check_particle_quality,
            self.check_counter_quality,
            self.check_keigo_quality
        ]
    
    def get_accuracy_summary(self):
        """精度統計のサマリーを取得"""
        if not self.accuracy_stats['correct_answer']:
            return None
        
        total_attempts = len(self.accuracy_stats['correct_answer'])
        correct_rate = sum(self.accuracy_stats['correct_answer']) / total_attempts * 100
        format_rate = sum(self.accuracy_stats['correct_format']) / len(self.accuracy_stats['correct_format']) * 100
        
        return {
            'total_attempts': total_attempts,
            'correct_rate': correct_rate,
            'format_rate': format_rate,
            'partial_rate': sum(self.accuracy_stats.get('partial_answer', [])) / total_attempts * 100,
            'no_answer_rate': sum(self.accuracy_stats.get('no_answer', [])) / total_attempts * 100
        }