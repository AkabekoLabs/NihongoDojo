"""
Colab環境用の可視化機能
"""

import os
import json
import time
import numpy as np
from datetime import datetime
from collections import defaultdict, deque
from IPython.display import clear_output, display
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from transformers import TrainerCallback
from .utils import setup_japanese_font


class GRPOVisualizationCallback(TrainerCallback):
    """GRPO学習の進捗をリアルタイムで可視化するコールバック"""
    
    def __init__(self, update_frequency=5, keep_history_steps=20, log_filename=None, logger=None):
        self.metrics_history = defaultdict(list)
        self.step_times = []
        self.start_time = time.time()
        self.last_step_time = time.time()
        self.update_frequency = update_frequency
        self.recent_logs = deque(maxlen=keep_history_steps)
        self.step_count = 0
        self.log_filename = log_filename
        self.logger = logger
        
        # 日本語フォントの設定
        setup_japanese_font()
    
    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs is not None:
            self.step_count += 1
            
            # 現在のステップ時間を記録
            current_time = time.time()
            step_duration = current_time - self.last_step_time
            self.last_step_time = current_time
            
            # メトリクスを記録
            for key, value in logs.items():
                if isinstance(value, (int, float)):
                    self.metrics_history[key].append(value)
            
            # ログを保存
            log_entry = {
                'step': state.global_step,
                'time': current_time - self.start_time,
                'duration': step_duration,
                'logs': logs.copy()
            }
            self.recent_logs.append(log_entry)
            
            # 履歴ファイルに保存
            if self.log_filename:
                history_entry = {
                    'step': state.global_step,
                    'timestamp': datetime.now().isoformat(),
                    'elapsed_time': current_time - self.start_time,
                    'metrics': {
                        'reward': logs.get('reward'),
                        'kl': logs.get('kl'),
                        'completion_length': logs.get('completion_length'),
                        'learning_rate': logs.get('learning_rate')
                    }
                }
                
                # 履歴ファイルに追記
                history_filename = self.log_filename.replace('.jsonl', '_history.jsonl')
                with open(history_filename, 'a', encoding='utf-8') as f:
                    json.dump(history_entry, f, ensure_ascii=False)
                    f.write('\n')
            
            # 指定された頻度で表示を更新
            if self.step_count % self.update_frequency == 0:
                self.update_display(args, state)
    
    def update_display(self, args, state):
        """表示を更新"""
        clear_output(wait=True)
        
        # 現在の進捗状況
        total_time = time.time() - self.start_time
        print(f"{'='*100}")
        print(f"🌸 GRPO学習進捗 - ステップ {state.global_step}/{args.max_steps} ({state.global_step/args.max_steps*100:.1f}%)")
        print(f"⏱️  総経過時間: {total_time:.1f}秒 | 平均ステップ時間: {total_time/state.global_step:.2f}秒")
        print(f"{'='*100}\n")
        
        # 最近のステップログを表示
        print("📋 最近のステップログ:")
        print("-"*100)
        for log_entry in list(self.recent_logs)[-5:]:  # 最新5ステップ分を表示
            print(f"ステップ {log_entry['step']:4d} | 時間: {log_entry['time']:6.1f}秒 | ", end="")
            if 'reward' in log_entry['logs']:
                print(f"報酬: {log_entry['logs']['reward']:+.4f} | ", end="")
            if 'completion_length' in log_entry['logs']:
                print(f"生成長: {log_entry['logs']['completion_length']:.0f} | ", end="")
            if 'kl' in log_entry['logs']:
                print(f"KL: {log_entry['logs']['kl']:.6f}", end="")
            print()
        print("-"*100 + "\n")
        
        # 現在のメトリクスサマリー
        if self.metrics_history['reward']:
            recent_rewards = self.metrics_history['reward'][-20:]  # 直近20ステップ
            print("📊 現在のパフォーマンス指標:")
            print(f"  🎯 報酬 - 現在: {recent_rewards[-1]:+.4f} | 平均: {np.mean(recent_rewards):+.4f} | 傾向: ", end="")
            if len(recent_rewards) > 1:
                trend = recent_rewards[-1] - recent_rewards[0]
                print("📈 上昇中" if trend > 0 else "📉 下降中")
            else:
                print("➡️ 評価中")
        
        # グラフを表示
        try:
            self.plot_metrics()
        except Exception as e:
            print(f"グラフ表示エラー: {str(e)}")
        
        # 一時停止オプション（重要なステップで）
        if state.global_step % 50 == 0:
            print(f"\n{'='*100}")
            print("💡 ヒント: 学習を中断したい場合は、カーネルの中断ボタンを押してください")
            print(f"{'='*100}")
    
    def plot_metrics(self):
        """メトリクスのグラフを表示"""
        if len(self.metrics_history['reward']) > 1:
            # 日本語フォントを明示的に設定
            import japanize_matplotlib
            plt.rcParams['font.family'] = 'IPAexGothic'
            
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            
            # タイトルを設定
            fig.suptitle('GRPO学習メトリクス（リアルタイム）', fontsize=16)
            
            # 1. 報酬の推移
            ax1 = axes[0, 0]
            steps = range(len(self.metrics_history['reward']))
            rewards = self.metrics_history['reward']
            
            # 生データ
            ax1.plot(steps, rewards, 'b-', alpha=0.3, linewidth=1, label='生データ')
            
            # 複数の移動平均
            for window, color, style in [(5, 'orange', '-'), (10, 'green', '--'), (20, 'red', ':')]:
                if len(rewards) > window:
                    moving_avg = np.convolve(rewards, np.ones(window)/window, mode='valid')
                    ax1.plot(range(window-1, len(steps)), moving_avg, color=color,
                            linestyle=style, linewidth=2, label=f'{window}ステップ平均')
            
            # 最高値と最低値をマーク
            max_idx = np.argmax(rewards)
            min_idx = np.argmin(rewards)
            ax1.scatter(max_idx, rewards[max_idx], color='gold', s=100, marker='*', zorder=5,
                       label=f'最大: {rewards[max_idx]:.3f}')
            ax1.scatter(min_idx, rewards[min_idx], color='purple', s=100, marker='v', zorder=5,
                       label=f'最小: {rewards[min_idx]:.3f}')
            
            ax1.set_title('総合報酬の推移')
            ax1.set_xlabel('ステップ')
            ax1.set_ylabel('報酬')
            ax1.grid(True, alpha=0.3)
            ax1.legend(loc='best')
            
            # 2. KLダイバージェンス
            if 'kl' in self.metrics_history and len(self.metrics_history['kl']) > 0:
                ax2 = axes[0, 1]
                kl_values = self.metrics_history['kl']
                ax2.semilogy(range(len(kl_values)), kl_values, 'g-', linewidth=2)
                ax2.fill_between(range(len(kl_values)), kl_values, alpha=0.3)
                
                ax2.set_title('KLダイバージェンス（モデルの変化度）')
                ax2.set_xlabel('ステップ')
                ax2.set_ylabel('KL（対数スケール）')
                ax2.grid(True, alpha=0.3)
                
                # 安全領域を表示
                ax2.axhline(y=0.01, color='orange', linestyle='--', label='注意')
                ax2.axhline(y=0.1, color='red', linestyle='--', label='危険')
                ax2.legend()
            
            # 3. 生成長の推移
            if 'completion_length' in self.metrics_history:
                ax3 = axes[1, 0]
                lengths = self.metrics_history['completion_length']
                ax3.plot(range(len(lengths)), lengths, 'm-', linewidth=1)
                
                # 移動平均
                if len(lengths) > 10:
                    moving_avg = np.convolve(lengths, np.ones(10)/10, mode='valid')
                    ax3.plot(range(9, len(lengths)), moving_avg, 'darkmagenta', linewidth=2,
                            label='10ステップ平均')
                
                ax3.set_title('生成トークン長の推移')
                ax3.set_xlabel('ステップ')
                ax3.set_ylabel('トークン数')
                ax3.grid(True, alpha=0.3)
                ax3.legend()
                
                # 目標範囲を表示
                ax3.axhspan(50, 150, alpha=0.2, color='green', label='理想範囲')
            
            # 4. 学習統計ダッシュボード
            ax4 = axes[1, 1]
            ax4.axis('off')
            
            # 統計情報をテキストで表示
            stats_text = "学習統計ダッシュボード\n\n"
            
            if self.metrics_history['reward']:
                rewards = self.metrics_history['reward']
                stats_text += "報酬統計:\n"
                stats_text += f"  - 現在値: {rewards[-1]:+.4f}\n"
                stats_text += f"  - 平均値: {np.mean(rewards):+.4f}\n"
                stats_text += f"  - 標準偏差: {np.std(rewards):.4f}\n"
                stats_text += f"  - 最大改善: {max(rewards) - rewards[0]:+.4f}\n\n"
                
                # 最近の傾向
                if len(rewards) > 10:
                    recent_trend = np.mean(rewards[-5:]) - np.mean(rewards[-10:-5])
                    stats_text += f"最近の傾向: {recent_trend:+.4f}\n"
                    stats_text += f"  {'改善中' if recent_trend > 0 else '低下中'}\n\n"
            
            if 'kl' in self.metrics_history and self.metrics_history['kl']:
                current_kl = self.metrics_history['kl'][-1]
                stats_text += f"KLダイバージェンス: {current_kl:.6f}\n"
                stats_text += f"  {'安定' if current_kl < 0.01 else '変化中' if current_kl < 0.1 else '注意'}\n"
            
            # 学習情報
            stats_text += "\n学習情報:\n"
            stats_text += "  - 日本語漢字学習タスク\n"
            stats_text += "  - フォーマット評価\n"
            stats_text += "  - 部分点による評価"
            
            ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes,
                    fontsize=11, verticalalignment='top',
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='lightblue', alpha=0.8))
            
            plt.tight_layout()
            plt.show()
    
    def get_summary_stats(self):
        """学習終了時のサマリー統計を取得"""
        summary = {}
        for metric, values in self.metrics_history.items():
            if values:
                summary[metric] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'min': np.min(values),
                    'max': np.max(values),
                    'final': values[-1],
                    'improvement': values[-1] - values[0] if len(values) > 1 else 0
                }
        return summary


def plot_training_history(history_filename):
    """保存された学習履歴からグラフを作成"""
    if not os.path.exists(history_filename):
        print(f"学習履歴ファイル {history_filename} が見つかりません。")
        return
    
    print("\n📈 学習履歴の可視化:")
    with open(history_filename, 'r', encoding='utf-8') as f:
        history_data = [json.loads(line) for line in f.readlines()]
    
    if not history_data:
        print("履歴データが空です。")
        return
    
    # データを整理
    steps = [d['step'] for d in history_data]
    rewards = [d['metrics']['reward'] for d in history_data if d['metrics']['reward'] is not None]
    kls = [d['metrics']['kl'] for d in history_data if d['metrics']['kl'] is not None]
    
    # グラフ作成
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # 報酬の推移
    ax1.plot(steps[:len(rewards)], rewards, 'b-', alpha=0.7)
    ax1.set_title('報酬の推移')
    ax1.set_xlabel('ステップ')
    ax1.set_ylabel('報酬')
    ax1.grid(True, alpha=0.3)
    
    # 移動平均を追加
    if len(rewards) > 20:
        window = 20
        moving_avg = np.convolve(rewards, np.ones(window)/window, mode='valid')
        ax1.plot(steps[window-1:len(moving_avg)+window-1], moving_avg, 'r-', linewidth=2, label='20ステップ移動平均')
        ax1.legend()
    
    # KLダイバージェンスの推移
    if kls:
        ax2.semilogy(steps[:len(kls)], kls, 'g-', alpha=0.7)
        ax2.set_title('KLダイバージェンスの推移')
        ax2.set_xlabel('ステップ')
        ax2.set_ylabel('KL（対数スケール）')
        ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    print(f"\n学習履歴データ数: {len(history_data)} ステップ")