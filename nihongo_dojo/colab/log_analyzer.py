"""
訓練ログの分析ユーティリティ
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from collections import defaultdict

# japanize_matplotlibを条件付きでインポート
try:
    import japanize_matplotlib
    JAPANIZE_AVAILABLE = True
except ImportError:
    JAPANIZE_AVAILABLE = False
    print("Warning: japanize_matplotlib not found. Japanese text in plots may not display correctly.")
    print("Install with: pip install japanize-matplotlib")


def analyze_training_logs(log_filename):
    """学習ログを分析する関数（ノートブック用）"""
    import os
    
    print("📊 学習ログの分析")
    print("="*50)
    
    # 基本ログファイルの分析
    if os.path.exists(log_filename):
        with open(log_filename, 'r', encoding='utf-8') as f:
            logs = [json.loads(line) for line in f]
        
        print(f"基本ログエントリ数: {len(logs)}")
        
        # 統計情報の計算
        rewards = []
        questions = []
        answers = []
        correct_answers = 0
        
        for log in logs:
            if 'rewards' in log and log['rewards']:
                rewards.extend(log['rewards'])
            if 'question' in log:
                questions.append(log['question'])
            if 'answer' in log and 'extracted' in log:
                answers.append((log['answer'], log['extracted']))
                if log['extracted'] and log['extracted'][0] == log['answer']:
                    correct_answers += 1
        
        if rewards:
            print(f"総報酬エントリ数: {len(rewards)}")
            print(f"平均報酬: {np.mean(rewards):.3f}")
            print(f"最大報酬: {np.max(rewards):.3f}")
            print(f"最小報酬: {np.min(rewards):.3f}")
        
        if answers:
            print(f"正答率: {correct_answers}/{len(answers)} ({correct_answers/len(answers)*100:.1f}%)")
        
        # 最新の10エントリを表示
        print(f"\n📋 最新の10エントリ:")
        for i, log in enumerate(logs[-10:]):
            print(f"  {i+1}. ステップ{log['step']}: {log['question'][:50]}...")
            if log['extracted'] and log['extracted'][0]:
                print(f"     → {log['extracted'][0]}")
            else:
                print(f"     → (回答なし)")
        
    else:
        print("基本ログファイルが見つかりません。")
    
    # 詳細ログファイルの分析
    detailed_log_file = log_filename.replace('.jsonl', '_detailed.jsonl')
    if os.path.exists(detailed_log_file):
        print(f"\n📊 詳細ログファイル: {detailed_log_file}")
        
        with open(detailed_log_file, 'r', encoding='utf-8') as f:
            detailed_logs = [json.loads(line) for line in f]
        
        print(f"詳細ログエントリ数: {len(detailed_logs)}")
        
        # 生成数の統計
        if detailed_logs:
            total_generations = sum(len(item['generations']) for log in detailed_logs for item in log['batch_data'])
            avg_generations_per_question = total_generations / sum(len(log['batch_data']) for log in detailed_logs)
            
            print(f"総生成数: {total_generations}")
            print(f"質問あたり平均生成数: {avg_generations_per_question:.1f}")
            
            # 最高報酬と最低報酬の例を表示
            all_generations = []
            for log in detailed_logs:
                for item in log['batch_data']:
                    for gen in item['generations']:
                        all_generations.append({
                            'question': item['question'],
                            'expected': item['expected_answer'],
                            'completion': gen['completion'],
                            'extracted': gen['extracted_answer'],
                            'reward': gen['reward']
                        })
            
            if all_generations:
                # 最高報酬の例
                best_gen = max(all_generations, key=lambda x: x['reward'])
                print(f"\n🏆 最高報酬の例 (報酬: {best_gen['reward']:.3f}):")
                print(f"質問: {best_gen['question']}")
                print(f"期待: {best_gen['expected']}")
                print(f"抽出: {best_gen['extracted']}")
                
                # 最低報酬の例
                worst_gen = min(all_generations, key=lambda x: x['reward'])
                print(f"\n❌ 最低報酬の例 (報酬: {worst_gen['reward']:.3f}):")
                print(f"質問: {worst_gen['question']}")
                print(f"期待: {worst_gen['expected']}")
                print(f"抽出: {worst_gen['extracted']}")
    
    else:
        print("\n詳細ログファイルが見つかりません。")


class TrainingLogAnalyzer:
    """訓練ログを分析するクラス"""
    
    def __init__(self, log_filename):
        """
        Args:
            log_filename: ログファイルのパス（.jsonl形式）
        """
        self.log_filename = log_filename
        self.logs = []
        self._load_logs()
    
    def _load_logs(self):
        """ログファイルを読み込む"""
        try:
            with open(self.log_filename, 'r', encoding='utf-8') as f:
                for line in f:
                    self.logs.append(json.loads(line.strip()))
        except FileNotFoundError:
            print(f"ログファイルが見つかりません: {self.log_filename}")
        except Exception as e:
            print(f"ログ読み込みエラー: {e}")
    
    def get_accuracy_stats(self):
        """精度統計を計算"""
        if not self.logs:
            return None
        
        total_entries = len(self.logs)
        correct_answers = sum(1 for log in self.logs 
                            if log.get('extracted', [None])[0] == log.get('answer'))
        
        # 抽出成功率
        extraction_success = sum(1 for log in self.logs 
                               if log.get('extracted', [None])[0] is not None)
        
        # 報酬の統計
        rewards = [log['rewards'][0] for log in self.logs if log.get('rewards')]
        
        return {
            'total_entries': total_entries,
            'correct_answers': correct_answers,
            'accuracy': correct_answers / total_entries * 100 if total_entries > 0 else 0,
            'extraction_success_rate': extraction_success / total_entries * 100 if total_entries > 0 else 0,
            'average_reward': np.mean(rewards) if rewards else 0,
            'max_reward': np.max(rewards) if rewards else 0,
            'min_reward': np.min(rewards) if rewards else 0,
            'std_reward': np.std(rewards) if rewards else 0
        }
    
    def get_question_type_analysis(self):
        """質問タイプ別の分析"""
        question_types = defaultdict(list)
        
        for log in self.logs:
            question = log.get('question', '')
            # 質問タイプを判定
            if '読み方' in question:
                q_type = '読み方'
            elif '漢字で書く' in question:
                q_type = '漢字書き'
            else:
                q_type = 'その他'
            
            is_correct = log.get('extracted', [None])[0] == log.get('answer')
            question_types[q_type].append({
                'correct': is_correct,
                'reward': log['rewards'][0] if log.get('rewards') else 0
            })
        
        # 統計を計算
        stats = {}
        for q_type, results in question_types.items():
            if results:
                correct_count = sum(1 for r in results if r['correct'])
                stats[q_type] = {
                    'count': len(results),
                    'accuracy': correct_count / len(results) * 100,
                    'avg_reward': np.mean([r['reward'] for r in results])
                }
        
        return stats
    
    def plot_training_progress(self, window_size=50):
        """訓練の進捗をプロット"""
        if not self.logs:
            print("ログデータがありません")
            return
        
        # 移動平均を計算
        rewards = [log['rewards'][0] for log in self.logs if log.get('rewards')]
        steps = list(range(len(rewards)))
        
        # 移動平均
        if len(rewards) >= window_size:
            moving_avg = pd.Series(rewards).rolling(window=window_size).mean()
        else:
            moving_avg = rewards
        
        # プロット
        plt.figure(figsize=(12, 6))
        
        # 報酬の推移
        plt.subplot(1, 2, 1)
        plt.plot(steps, rewards, alpha=0.3, label='生の報酬')
        if len(rewards) >= window_size:
            plt.plot(steps, moving_avg, label=f'{window_size}ステップ移動平均')
        plt.xlabel('ステップ')
        plt.ylabel('報酬')
        plt.title('報酬の推移')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 正答率の推移
        plt.subplot(1, 2, 2)
        accuracies = []
        for i in range(0, len(self.logs), window_size):
            batch = self.logs[i:i+window_size]
            correct = sum(1 for log in batch 
                        if log.get('extracted', [None])[0] == log.get('answer'))
            accuracy = correct / len(batch) * 100 if batch else 0
            accuracies.append(accuracy)
        
        acc_steps = list(range(0, len(self.logs), window_size))
        plt.plot(acc_steps, accuracies, marker='o')
        plt.xlabel('ステップ')
        plt.ylabel('正答率 (%)')
        plt.title(f'{window_size}ステップごとの正答率')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def get_error_analysis(self, num_samples=10):
        """エラー分析（間違えた例を抽出）"""
        errors = []
        
        for log in self.logs:
            extracted = log.get('extracted', [None])[0]
            answer = log.get('answer')
            
            if extracted != answer:
                errors.append({
                    'step': log.get('step'),
                    'question': log.get('question'),
                    'expected': answer,
                    'got': extracted,
                    'response': log.get('responses', [''])[0][:200] + '...' if log.get('responses') else '',
                    'reward': log.get('rewards', [0])[0]
                })
        
        # 報酬が低い順にソート
        errors.sort(key=lambda x: x['reward'])
        
        return errors[:num_samples]
    
    def print_summary(self):
        """サマリーを表示"""
        print("=" * 80)
        print("訓練ログ分析サマリー")
        print("=" * 80)
        
        # 基本統計
        stats = self.get_accuracy_stats()
        if stats:
            print(f"\n📊 基本統計:")
            print(f"  総エントリ数: {stats['total_entries']}")
            print(f"  正答数: {stats['correct_answers']}")
            print(f"  正答率: {stats['accuracy']:.2f}%")
            print(f"  抽出成功率: {stats['extraction_success_rate']:.2f}%")
            print(f"  平均報酬: {stats['average_reward']:.3f}")
            print(f"  最大報酬: {stats['max_reward']:.3f}")
            print(f"  最小報酬: {stats['min_reward']:.3f}")
        
        # 質問タイプ別分析
        type_stats = self.get_question_type_analysis()
        if type_stats:
            print(f"\n📝 質問タイプ別分析:")
            for q_type, stat in type_stats.items():
                print(f"  {q_type}:")
                print(f"    - 件数: {stat['count']}")
                print(f"    - 正答率: {stat['accuracy']:.2f}%")
                print(f"    - 平均報酬: {stat['avg_reward']:.3f}")
        
        # エラー例
        errors = self.get_error_analysis(5)
        if errors:
            print(f"\n❌ エラー例（報酬が低い順）:")
            for i, error in enumerate(errors, 1):
                print(f"\n  {i}. ステップ {error['step']}:")
                print(f"     質問: {error['question']}")
                print(f"     期待: {error['expected']}")
                print(f"     取得: {error['got']}")
                print(f"     報酬: {error['reward']:.3f}")


def analyze_training_logs(log_filename):
    """訓練ログを分析する便利関数"""
    analyzer = TrainingLogAnalyzer(log_filename)
    analyzer.print_summary()
    analyzer.plot_training_progress()
    return analyzer