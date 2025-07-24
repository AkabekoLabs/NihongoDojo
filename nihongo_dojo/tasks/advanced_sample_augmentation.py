"""
Advanced and Cultural tasks sample augmentation module for Nihongo DoJo
高度・文化的タスクのサンプル数を大幅に増幅するモジュール
"""

from typing import Dict, List, Tuple
from ..core import TaskDifficulty


class AdvancedTaskSampleAugmenter:
    """高度なタスクサンプルの増幅を行うクラス"""
    
    @staticmethod
    def get_augmented_onomatopoeia_examples() -> Dict[str, List[Tuple]]:
        """拡張されたオノマトペの例を取得"""
        return {
            "giongo": [  # 擬音語（実際の音）
                ("ワンワン", "犬の鳴き声", "dogs barking"),
                ("ニャーニャー", "猫の鳴き声", "cats meowing"),
                ("ガタガタ", "物が揺れる音", "rattling sound"),
                ("ドンドン", "ドアを叩く音", "knocking sound"),
                ("ザーザー", "雨が降る音", "sound of heavy rain"),
                ("ゴロゴロ", "雷の音", "thunder rumbling"),
                ("パチパチ", "拍手の音", "clapping sound"),
                ("カチカチ", "時計の音", "ticking sound"),
                ("ブーブー", "車のクラクション", "car horn"),
                ("ピンポン", "ドアベルの音", "doorbell sound"),
                ("チリンチリン", "鈴の音", "bell ringing"),
                ("ガラガラ", "物が崩れる音", "crashing sound"),
                ("シュー", "蒸気の音", "steam hissing"),
                ("ポタポタ", "水滴の音", "dripping water"),
                ("バタバタ", "慌ただしい音", "flapping/rushing sound")
            ],
            "gitaigo": [  # 擬態語（様子）
                ("キラキラ", "光っている様子", "sparkling/glittering"),
                ("ツルツル", "滑らかな様子", "smooth/slippery"),
                ("ピカピカ", "光り輝く様子", "shiny/gleaming"),
                ("フワフワ", "柔らかい様子", "fluffy/soft"),
                ("ベタベタ", "粘着する様子", "sticky"),
                ("サラサラ", "さらさらした様子", "smooth-flowing"),
                ("ゴツゴツ", "でこぼこした様子", "rough/rugged"),
                ("ネバネバ", "粘り気のある様子", "slimy/sticky"),
                ("ペラペラ", "薄い様子・流暢に話す様子", "thin/fluent"),
                ("ボロボロ", "ぼろぼろの様子", "tattered/worn out"),
                ("プリプリ", "弾力のある様子", "bouncy/elastic"),
                ("カチカチ", "硬い様子", "hard/stiff"),
                ("ヌルヌル", "ぬるぬるした様子", "slimy"),
                ("ザラザラ", "粗い様子", "rough/coarse"),
                ("モチモチ", "もちもちした食感", "chewy/springy")
            ],
            "gijougo": [  # 擬情語（感情・感覚）
                ("ドキドキ", "緊張・興奮", "heart pounding"),
                ("ワクワク", "期待・楽しみ", "excited/thrilled"),
                ("イライラ", "いらだち", "irritated/frustrated"),
                ("ソワソワ", "落ち着かない", "restless/fidgety"),
                ("ウキウキ", "嬉しい気持ち", "cheerful/happy"),
                ("ハラハラ", "心配・不安", "anxious/worried"),
                ("ムカムカ", "腹立たしい", "annoyed/nauseous"),
                ("ビクビク", "びくびくする", "nervous/scared"),
                ("ニコニコ", "にこやかな様子", "smiling happily"),
                ("オドオド", "おどおどする", "timid/nervous"),
                ("ウトウト", "眠そうな様子", "drowsy/dozing"),
                ("ガッカリ", "失望", "disappointed"),
                ("スッキリ", "爽快な気分", "refreshed"),
                ("モヤモヤ", "もやもやした気持ち", "unclear feeling"),
                ("ゾクゾク", "寒気・興奮", "shivering/thrilled")
            ],
            "giseigo": [  # 擬声語（人や動物の声）
                ("ヒソヒソ", "ひそひそ話", "whispering"),
                ("ペチャクチャ", "おしゃべり", "chattering"),
                ("ブツブツ", "つぶやく", "muttering"),
                ("ワイワイ", "にぎやかに話す", "talking noisily"),
                ("ガヤガヤ", "大勢の話し声", "noisy chatter"),
                ("クスクス", "くすくす笑う", "giggling"),
                ("ゲラゲラ", "大笑いする", "laughing loudly"),
                ("シクシク", "泣く", "sobbing"),
                ("ワーワー", "大声で泣く", "crying loudly"),
                ("フンフン", "鼻歌", "humming"),
                ("ブーブー", "不満を言う", "complaining"),
                ("ペロペロ", "舐める音", "licking sound"),
                ("ゴクゴク", "飲む音", "gulping sound"),
                ("モグモグ", "食べる様子", "chewing"),
                ("ハァハァ", "息切れ", "panting")
            ]
        }
    
    @staticmethod
    def get_augmented_conversation_examples() -> Dict[str, List[Dict]]:
        """拡張された会話例を取得"""
        return {
            "aizuchi": [  # 相槌
                {
                    "context": "友達が旅行の話をしている時",
                    "responses": ["へー、そうなんだ", "いいね！", "楽しそう！", "それで？"],
                    "formal_responses": ["そうですか", "いいですね", "楽しそうですね", "それからどうなりましたか"]
                },
                {
                    "context": "同僚が仕事の苦労を話している時",
                    "responses": ["大変だね", "お疲れ様", "それは困ったね", "わかるよ"],
                    "formal_responses": ["大変ですね", "お疲れ様です", "それは困りましたね", "わかります"]
                },
                {
                    "context": "上司が指示を出している時",
                    "responses": ["はい", "わかりました", "承知しました", "了解です"],
                    "formal_responses": ["はい、承知いたしました", "かしこまりました", "承りました", "了解いたしました"]
                },
                {
                    "context": "先生が説明している時",
                    "responses": ["なるほど", "そういうことか", "わかりました", "勉強になります"],
                    "formal_responses": ["なるほど、そういうことですね", "理解できました", "よくわかりました", "大変勉強になります"]
                },
                {
                    "context": "お客様が要望を伝えている時",
                    "responses": ["確かに", "ごもっともです", "おっしゃる通りです", "そのようにいたします"],
                    "formal_responses": ["確かにそうですね", "ごもっともでございます", "おっしゃる通りでございます", "そのように対応させていただきます"]
                }
            ],
            "requests": [  # 依頼
                {
                    "situation": "資料のコピーを頼む",
                    "casual": "これ、コピーしてもらえる？",
                    "polite": "すみません、これをコピーしていただけますか？",
                    "formal": "恐れ入りますが、こちらの資料をコピーしていただけますでしょうか？"
                },
                {
                    "situation": "会議の日程変更を頼む",
                    "casual": "会議の日、変えてもらえない？",
                    "polite": "会議の日程を変更していただけませんか？",
                    "formal": "大変恐縮ですが、会議の日程を変更していただくことは可能でしょうか？"
                },
                {
                    "situation": "レポートの確認を頼む",
                    "casual": "このレポート、見てくれる？",
                    "polite": "このレポートを確認していただけますか？",
                    "formal": "お忙しいところ申し訳ございませんが、こちらのレポートをご確認いただけますでしょうか？"
                },
                {
                    "situation": "電話番号を教えてもらう",
                    "casual": "電話番号教えて",
                    "polite": "電話番号を教えていただけますか？",
                    "formal": "恐れ入りますが、お電話番号をお教えいただけますでしょうか？"
                },
                {
                    "situation": "道を尋ねる",
                    "casual": "駅はどっち？",
                    "polite": "すみません、駅はどちらですか？",
                    "formal": "恐れ入りますが、駅への行き方を教えていただけますでしょうか？"
                },
                {
                    "situation": "手伝いを頼む",
                    "casual": "ちょっと手伝って",
                    "polite": "手伝っていただけませんか？",
                    "formal": "お手数をおかけしますが、お手伝いいただけますでしょうか？"
                },
                {
                    "situation": "説明を求める",
                    "casual": "これ、どういうこと？",
                    "polite": "これについて説明していただけますか？",
                    "formal": "恐れ入りますが、こちらについてご説明いただけますでしょうか？"
                }
            ],
            "refusals": [  # 断り方
                {
                    "situation": "飲み会の誘いを断る",
                    "direct": "今日は無理です",
                    "polite": "申し訳ありませんが、今日は都合が悪いです",
                    "indirect": "今日はちょっと...また今度お願いします"
                },
                {
                    "situation": "仕事の依頼を断る",
                    "direct": "それはできません",
                    "polite": "申し訳ございませんが、対応が難しいです",
                    "indirect": "今、他の案件で手一杯でして..."
                },
                {
                    "situation": "借金の申し出を断る",
                    "direct": "お金は貸せません",
                    "polite": "申し訳ありませんが、お力になれません",
                    "indirect": "私も今月は厳しくて..."
                },
                {
                    "situation": "週末の予定を断る",
                    "direct": "その日は予定があります",
                    "polite": "申し訳ありませんが、その日は先約があります",
                    "indirect": "その日はちょっと都合が..."
                }
            ],
            "phone": [  # 電話対応
                {
                    "situation": "電話を受ける（ビジネス）",
                    "opening": "お電話ありがとうございます。〇〇会社の△△です。",
                    "closing": "お電話ありがとうございました。失礼いたします。",
                    "transfer": "少々お待ちください。担当者におつなぎいたします。"
                },
                {
                    "situation": "電話をかける（ビジネス）",
                    "opening": "お忙しいところ恐れ入ります。〇〇会社の△△と申します。",
                    "purpose": "〜の件でお電話させていただきました。",
                    "closing": "お忙しいところありがとうございました。失礼いたします。"
                },
                {
                    "situation": "不在時の対応",
                    "response": "申し訳ございません。〇〇は席を外しております。",
                    "message": "よろしければ、ご伝言を承りますが。",
                    "callback": "折り返しお電話させていただきましょうか。"
                },
                {
                    "situation": "間違い電話",
                    "response": "申し訳ございません。お電話番号をお間違えのようです。",
                    "confirm": "こちらは〇〇〇-〇〇〇〇ですが。",
                    "closing": "いえいえ、お気になさらないでください。"
                }
            ],
            "apologies": [  # 謝罪
                {
                    "situation": "遅刻の謝罪",
                    "casual": "遅れてごめん",
                    "polite": "遅れてすみません",
                    "formal": "遅れまして大変申し訳ございません",
                    "business": "お待たせして誠に申し訳ございません"
                },
                {
                    "situation": "ミスの謝罪",
                    "casual": "間違えちゃった、ごめん",
                    "polite": "間違えてしまい、すみません",
                    "formal": "私のミスで申し訳ございません",
                    "business": "この度は私の不手際により、ご迷惑をおかけして誠に申し訳ございません"
                },
                {
                    "situation": "断りの謝罪",
                    "casual": "ごめん、無理だわ",
                    "polite": "申し訳ありませんが、難しいです",
                    "formal": "大変申し訳ございませんが、お受けできません",
                    "business": "せっかくのお申し出ですが、今回は見送らせていただきます"
                }
            ]
        }
    
    @staticmethod
    def get_augmented_proverb_idiom_examples() -> Dict[str, List[Dict]]:
        """拡張されたことわざ・慣用句の例を取得"""
        return {
            "proverbs": [
                {
                    "proverb": "猿も木から落ちる",
                    "reading": "さるもきからおちる",
                    "meaning": "どんなに上手な人でも時には失敗する",
                    "usage": "プロでも失敗することがある。猿も木から落ちるというものだ。"
                },
                {
                    "proverb": "石の上にも三年",
                    "reading": "いしのうえにもさんねん",
                    "meaning": "辛いことでも我慢して続ければ成功する",
                    "usage": "すぐに結果は出ない。石の上にも三年だよ。"
                },
                {
                    "proverb": "急がば回れ",
                    "reading": "いそがばまわれ",
                    "meaning": "急ぐときほど安全な道を選ぶべき",
                    "usage": "近道は危険だ。急がば回れで、安全な道を行こう。"
                },
                {
                    "proverb": "塵も積もれば山となる",
                    "reading": "ちりもつもればやまとなる",
                    "meaning": "小さなことでも積み重ねれば大きくなる",
                    "usage": "毎日少しずつ貯金しよう。塵も積もれば山となるからね。"
                },
                {
                    "proverb": "七転び八起き",
                    "reading": "ななころびやおき",
                    "meaning": "何度失敗してもあきらめずに立ち上がる",
                    "usage": "失敗を恐れるな。七転び八起きの精神で頑張ろう。"
                },
                {
                    "proverb": "花より団子",
                    "reading": "はなよりだんご",
                    "meaning": "風流よりも実利を重んじる",
                    "usage": "桜は綺麗だけど、私は花より団子で、お弁当が楽しみ。"
                },
                {
                    "proverb": "郷に入っては郷に従え",
                    "reading": "ごうにいってはごうにしたがえ",
                    "meaning": "その土地の習慣に従うべき",
                    "usage": "外国では、郷に入っては郷に従えで、現地の習慣を尊重しよう。"
                },
                {
                    "proverb": "井の中の蛙大海を知らず",
                    "reading": "いのなかのかわずたいかいをしらず",
                    "meaning": "狭い世界しか知らない人",
                    "usage": "もっと広い世界を見ないと、井の中の蛙大海を知らずになってしまう。"
                },
                {
                    "proverb": "二兎を追う者は一兎をも得ず",
                    "reading": "にとをおうものはいっとをもえず",
                    "meaning": "欲張ると何も得られない",
                    "usage": "あれもこれもやろうとすると、二兎を追う者は一兎をも得ずだよ。"
                },
                {
                    "proverb": "明日は明日の風が吹く",
                    "reading": "あしたはあしたのかぜがふく",
                    "meaning": "明日のことは明日考えればよい",
                    "usage": "今日のことで精一杯。明日は明日の風が吹くさ。"
                }
            ],
            "idioms": [
                {
                    "idiom": "目から鱗が落ちる",
                    "reading": "めからうろこがおちる",
                    "meaning": "今まで分からなかったことが急に理解できる",
                    "usage": "先生の説明を聞いて、目から鱗が落ちた。"
                },
                {
                    "idiom": "腹が立つ",
                    "reading": "はらがたつ",
                    "meaning": "怒る",
                    "usage": "彼の態度には本当に腹が立つ。"
                },
                {
                    "idiom": "水に流す",
                    "reading": "みずにながす",
                    "meaning": "過去のことを忘れて許す",
                    "usage": "もう済んだことだから、水に流そう。"
                },
                {
                    "idiom": "首を長くして待つ",
                    "reading": "くびをながくしてまつ",
                    "meaning": "楽しみに待つ",
                    "usage": "新作ゲームの発売を首を長くして待っている。"
                },
                {
                    "idiom": "顔が広い",
                    "reading": "かおがひろい",
                    "meaning": "知り合いが多い",
                    "usage": "彼は業界で顔が広いから、誰でも知っている。"
                },
                {
                    "idiom": "手を焼く",
                    "reading": "てをやく",
                    "meaning": "扱いに困る",
                    "usage": "やんちゃな子供に手を焼いている。"
                },
                {
                    "idiom": "頭が痛い",
                    "reading": "あたまがいたい",
                    "meaning": "悩ましい問題",
                    "usage": "この問題の解決策が見つからなくて頭が痛い。"
                },
                {
                    "idiom": "足を引っ張る",
                    "reading": "あしをひっぱる",
                    "meaning": "邪魔をする",
                    "usage": "チームの足を引っ張らないように頑張る。"
                },
                {
                    "idiom": "口が軽い",
                    "reading": "くちがかるい",
                    "meaning": "秘密を守れない",
                    "usage": "彼は口が軽いから、秘密は教えられない。"
                },
                {
                    "idiom": "気が重い",
                    "reading": "きがおもい",
                    "meaning": "気分が沈む、憂鬱",
                    "usage": "明日のプレゼンを考えると気が重い。"
                }
            ],
            "yojijukugo": [  # 四字熟語
                {
                    "yojijukugo": "一期一会",
                    "reading": "いちごいちえ",
                    "meaning": "一生に一度の出会いを大切にする",
                    "usage": "この出会いも一期一会、大切にしよう。"
                },
                {
                    "yojijukugo": "十人十色",
                    "reading": "じゅうにんといろ",
                    "meaning": "人それぞれ好みや考えが違う",
                    "usage": "意見が分かれるのは当然。十人十色だから。"
                },
                {
                    "yojijukugo": "自業自得",
                    "reading": "じごうじとく",
                    "meaning": "自分の行いの結果を自分で受ける",
                    "usage": "準備を怠った結果だ。自業自得だね。"
                },
                {
                    "yojijukugo": "切磋琢磨",
                    "reading": "せっさたくま",
                    "meaning": "互いに励まし合って向上する",
                    "usage": "ライバルと切磋琢磨して成長した。"
                },
                {
                    "yojijukugo": "温故知新",
                    "reading": "おんこちしん",
                    "meaning": "古いことを学んで新しい知識を得る",
                    "usage": "歴史を学ぶことは温故知新の精神だ。"
                }
            ]
        }
    
    @staticmethod
    def get_augmented_business_japanese_examples() -> Dict[str, List[Dict]]:
        """拡張されたビジネス日本語の例を取得"""
        return {
            "email": {
                "openings": [
                    "いつもお世話になっております。",
                    "平素より大変お世話になっております。",
                    "お忙しいところ恐れ入ります。",
                    "ご無沙汰しております。",
                    "先日はありがとうございました。",
                    "早速のご返信ありがとうございます。",
                    "お問い合わせいただきありがとうございます。",
                    "ご連絡いただきありがとうございます。"
                ],
                "closings": [
                    "よろしくお願いいたします。",
                    "ご検討のほど、よろしくお願いいたします。",
                    "ご確認のほど、よろしくお願いいたします。",
                    "今後ともよろしくお願いいたします。",
                    "ご多忙とは存じますが、よろしくお願いいたします。",
                    "お手数をおかけしますが、よろしくお願いいたします。",
                    "ご不明な点がございましたら、お気軽にお問い合わせください。",
                    "取り急ぎご連絡まで。"
                ],
                "phrases": [
                    "添付ファイルをご確認ください。",
                    "下記の通りご報告いたします。",
                    "ご都合はいかがでしょうか。",
                    "恐れ入りますが、〜していただけますでしょうか。",
                    "大変申し訳ございませんが、〜",
                    "お忙しいところ恐縮ですが、〜",
                    "ご確認いただければ幸いです。",
                    "ご返信をお待ちしております。",
                    "お手数をおかけして申し訳ございません。",
                    "ご理解のほど、よろしくお願いいたします。"
                ]
            },
            "presentation": {
                "opening": [
                    "本日は貴重なお時間をいただき、ありがとうございます。",
                    "〇〇について発表させていただきます。",
                    "それでは始めさせていただきます。",
                    "本日の議題は〜です。"
                ],
                "transition": [
                    "次に〜について説明します。",
                    "続きまして〜",
                    "ここで〜に移ります。",
                    "それでは〜を見ていきましょう。",
                    "この点について詳しく説明します。"
                ],
                "closing": [
                    "以上で発表を終わります。",
                    "ご清聴ありがとうございました。",
                    "ご質問はございますか。",
                    "何かご不明な点がございましたら、お聞きください。"
                ]
            },
            "meeting": {
                "starting": [
                    "それでは会議を始めさせていただきます。",
                    "本日の議題は〜です。",
                    "まず〜から始めましょう。",
                    "お忙しい中お集まりいただき、ありがとうございます。"
                ],
                "opinions": [
                    "私の意見では〜",
                    "〜と思うのですが、いかがでしょうか。",
                    "〜という考えもあります。",
                    "〜について提案があります。",
                    "別の見方をすれば〜"
                ],
                "agreement": [
                    "おっしゃる通りです。",
                    "同感です。",
                    "なるほど、そういう考え方もありますね。",
                    "賛成です。",
                    "良いアイデアだと思います。"
                ],
                "disagreement": [
                    "その点については少し違う意見があります。",
                    "確かにそうですが、一方で〜",
                    "別の視点から見ると〜",
                    "懸念される点があります。",
                    "もう少し検討が必要かもしれません。"
                ]
            },
            "negotiation": [
                {
                    "phrase": "条件について相談させていただきたいのですが",
                    "context": "交渉開始",
                    "formal_level": "high"
                },
                {
                    "phrase": "もう少しご検討いただけませんでしょうか",
                    "context": "再考依頼",
                    "formal_level": "high"
                },
                {
                    "phrase": "双方にとって良い条件を見つけましょう",
                    "context": "妥協案提示",
                    "formal_level": "medium"
                },
                {
                    "phrase": "この条件でいかがでしょうか",
                    "context": "提案",
                    "formal_level": "medium"
                }
            ]
        }
    
    @staticmethod
    def get_augmented_classical_japanese_examples() -> Dict[str, List[Dict]]:
        """拡張された古典日本語の例を取得"""
        return {
            "auxiliary_verbs": [
                {
                    "classical": "あり",
                    "modern": "ある",
                    "type": "存在",
                    "example": "都にありし人",
                    "translation": "都にいた人"
                },
                {
                    "classical": "をり",
                    "modern": "いる",
                    "type": "存在",
                    "example": "家にをりける時",
                    "translation": "家にいた時"
                },
                {
                    "classical": "なり",
                    "modern": "である",
                    "type": "断定",
                    "example": "これは本なり",
                    "translation": "これは本である"
                },
                {
                    "classical": "たり",
                    "modern": "である",
                    "type": "断定",
                    "example": "勇敢なる武士たり",
                    "translation": "勇敢な武士である"
                },
                {
                    "classical": "けり",
                    "modern": "〜た",
                    "type": "過去・詠嘆",
                    "example": "昔、男ありけり",
                    "translation": "昔、男がいた"
                },
                {
                    "classical": "き",
                    "modern": "〜た",
                    "type": "過去回想",
                    "example": "見し夢",
                    "translation": "見た夢"
                },
                {
                    "classical": "つ",
                    "modern": "〜た",
                    "type": "完了",
                    "example": "書きつ",
                    "translation": "書いた"
                },
                {
                    "classical": "ぬ",
                    "modern": "〜た",
                    "type": "完了",
                    "example": "散りぬ",
                    "translation": "散った"
                },
                {
                    "classical": "たし",
                    "modern": "〜たい",
                    "type": "希望",
                    "example": "見たし",
                    "translation": "見たい"
                },
                {
                    "classical": "べし",
                    "modern": "〜べきだ、〜だろう",
                    "type": "推量・当然",
                    "example": "行くべし",
                    "translation": "行くべきだ"
                },
                {
                    "classical": "らむ",
                    "modern": "〜だろう",
                    "type": "現在推量",
                    "example": "今頃は着きたらむ",
                    "translation": "今頃は着いただろう"
                },
                {
                    "classical": "めり",
                    "modern": "〜ようだ",
                    "type": "推定",
                    "example": "雨降るめり",
                    "translation": "雨が降るようだ"
                }
            ],
            "particles": [
                {
                    "classical": "の",
                    "modern": "が",
                    "usage": "主格",
                    "example": "我の行く道",
                    "translation": "私が行く道"
                },
                {
                    "classical": "が",
                    "modern": "の",
                    "usage": "連体格",
                    "example": "君が代",
                    "translation": "君の代"
                },
                {
                    "classical": "に",
                    "modern": "へ、に",
                    "usage": "方向",
                    "example": "都に上る",
                    "translation": "都へ上る"
                },
                {
                    "classical": "より",
                    "modern": "から",
                    "usage": "起点",
                    "example": "東より来る",
                    "translation": "東から来る"
                },
                {
                    "classical": "にて",
                    "modern": "で",
                    "usage": "場所・手段",
                    "example": "庭にて遊ぶ",
                    "translation": "庭で遊ぶ"
                },
                {
                    "classical": "ぞ",
                    "modern": "〜だ",
                    "usage": "強調",
                    "example": "これぞ真実なる",
                    "translation": "これこそ真実だ"
                },
                {
                    "classical": "こそ",
                    "modern": "〜こそ",
                    "usage": "強調",
                    "example": "今こそ行かめ",
                    "translation": "今こそ行こう"
                },
                {
                    "classical": "や",
                    "modern": "〜か",
                    "usage": "疑問",
                    "example": "誰や来る",
                    "translation": "誰が来るか"
                }
            ],
            "kakari_musubi": [
                {
                    "kakari": "ぞ",
                    "musubi": "連体形",
                    "example": "花ぞ咲きける",
                    "translation": "花が咲いた"
                },
                {
                    "kakari": "なむ",
                    "musubi": "連体形",
                    "example": "雨なむ降りける",
                    "translation": "雨が降った"
                },
                {
                    "kakari": "こそ",
                    "musubi": "已然形",
                    "example": "春こそ来れ",
                    "translation": "春が来た"
                },
                {
                    "kakari": "や",
                    "musubi": "連体形",
                    "example": "誰や来る",
                    "translation": "誰が来るか"
                },
                {
                    "kakari": "か",
                    "musubi": "連体形",
                    "example": "いづれか良き",
                    "translation": "どれが良いか"
                }
            ],
            "famous_texts": [
                {
                    "title": "竹取物語",
                    "text": "今は昔、竹取の翁といふ者ありけり。",
                    "translation": "今となっては昔のこと、竹取の翁という者がいた。",
                    "period": "平安初期"
                },
                {
                    "title": "源氏物語",
                    "text": "いづれの御時にか、女御、更衣あまた候ひ給ひける中に",
                    "translation": "どの帝の御代であったか、女御や更衣が大勢お仕えしていた中に",
                    "period": "平安中期"
                },
                {
                    "title": "枕草子",
                    "text": "春はあけぼの。やうやう白くなりゆく山際",
                    "translation": "春は明け方がよい。だんだん白くなっていく山際",
                    "period": "平安中期"
                },
                {
                    "title": "徒然草",
                    "text": "つれづれなるままに、日暮らし、硯にむかひて",
                    "translation": "することもなく退屈なままに、一日中、硯に向かって",
                    "period": "鎌倉末期"
                },
                {
                    "title": "平家物語",
                    "text": "祇園精舎の鐘の声、諸行無常の響きあり",
                    "translation": "祇園精舎の鐘の音は、諸行無常の響きがある",
                    "period": "鎌倉時代"
                }
            ]
        }
    
    @staticmethod
    def get_augmented_specialized_vocabulary_examples() -> Dict[str, List[Dict]]:
        """拡張された専門用語の例を取得"""
        return {
            "technology": [
                {
                    "term": "人工知能",
                    "reading": "じんこうちのう",
                    "english": "artificial intelligence",
                    "definition": "人間の知的能力をコンピュータで実現する技術"
                },
                {
                    "term": "機械学習",
                    "reading": "きかいがくしゅう",
                    "english": "machine learning",
                    "definition": "データから自動的に学習するアルゴリズム"
                },
                {
                    "term": "深層学習",
                    "reading": "しんそうがくしゅう",
                    "english": "deep learning",
                    "definition": "多層ニューラルネットワークを用いた機械学習"
                },
                {
                    "term": "仮想現実",
                    "reading": "かそうげんじつ",
                    "english": "virtual reality",
                    "definition": "コンピュータで作られた仮想的な世界"
                },
                {
                    "term": "拡張現実",
                    "reading": "かくちょうげんじつ",
                    "english": "augmented reality",
                    "definition": "現実世界にデジタル情報を重ね合わせる技術"
                },
                {
                    "term": "量子コンピュータ",
                    "reading": "りょうしコンピュータ",
                    "english": "quantum computer",
                    "definition": "量子力学の原理を利用した計算機"
                },
                {
                    "term": "ブロックチェーン",
                    "reading": "ブロックチェーン",
                    "english": "blockchain",
                    "definition": "分散型台帳技術"
                },
                {
                    "term": "クラウドコンピューティング",
                    "reading": "クラウドコンピューティング",
                    "english": "cloud computing",
                    "definition": "インターネット経由でコンピューティングサービスを提供"
                },
                {
                    "term": "ビッグデータ",
                    "reading": "ビッグデータ",
                    "english": "big data",
                    "definition": "従来の方法では処理できない大規模データ"
                },
                {
                    "term": "サイバーセキュリティ",
                    "reading": "サイバーセキュリティ",
                    "english": "cybersecurity",
                    "definition": "コンピュータシステムの安全性確保"
                }
            ],
            "medical": [
                {
                    "term": "診断",
                    "reading": "しんだん",
                    "english": "diagnosis",
                    "definition": "病気や健康状態を判定すること"
                },
                {
                    "term": "治療",
                    "reading": "ちりょう",
                    "english": "treatment",
                    "definition": "病気を治すための医療行為"
                },
                {
                    "term": "症状",
                    "reading": "しょうじょう",
                    "english": "symptom",
                    "definition": "病気の現れ"
                },
                {
                    "term": "予防接種",
                    "reading": "よぼうせっしゅ",
                    "english": "vaccination",
                    "definition": "病気を予防するための注射"
                },
                {
                    "term": "抗体",
                    "reading": "こうたい",
                    "english": "antibody",
                    "definition": "病原体に対抗する免疫物質"
                },
                {
                    "term": "感染症",
                    "reading": "かんせんしょう",
                    "english": "infectious disease",
                    "definition": "病原体によって引き起こされる病気"
                },
                {
                    "term": "慢性疾患",
                    "reading": "まんせいしっかん",
                    "english": "chronic disease",
                    "definition": "長期間続く病気"
                },
                {
                    "term": "手術",
                    "reading": "しゅじゅつ",
                    "english": "surgery",
                    "definition": "外科的治療"
                },
                {
                    "term": "処方箋",
                    "reading": "しょほうせん",
                    "english": "prescription",
                    "definition": "医師が薬を指示する文書"
                },
                {
                    "term": "副作用",
                    "reading": "ふくさよう",
                    "english": "side effect",
                    "definition": "薬の望ましくない作用"
                }
            ],
            "legal": [
                {
                    "term": "契約",
                    "reading": "けいやく",
                    "english": "contract",
                    "definition": "法的拘束力のある合意"
                },
                {
                    "term": "訴訟",
                    "reading": "そしょう",
                    "english": "lawsuit",
                    "definition": "裁判所での法的争い"
                },
                {
                    "term": "弁護士",
                    "reading": "べんごし",
                    "english": "lawyer",
                    "definition": "法律の専門家"
                },
                {
                    "term": "判決",
                    "reading": "はんけつ",
                    "english": "judgment",
                    "definition": "裁判所の決定"
                },
                {
                    "term": "証拠",
                    "reading": "しょうこ",
                    "english": "evidence",
                    "definition": "事実を証明する材料"
                },
                {
                    "term": "法廷",
                    "reading": "ほうてい",
                    "english": "court",
                    "definition": "裁判を行う場所"
                },
                {
                    "term": "被告",
                    "reading": "ひこく",
                    "english": "defendant",
                    "definition": "訴えられた人"
                },
                {
                    "term": "原告",
                    "reading": "げんこく",
                    "english": "plaintiff",
                    "definition": "訴えた人"
                },
                {
                    "term": "和解",
                    "reading": "わかい",
                    "english": "settlement",
                    "definition": "争いを話し合いで解決"
                },
                {
                    "term": "賠償",
                    "reading": "ばいしょう",
                    "english": "compensation",
                    "definition": "損害の補償"
                }
            ],
            "finance": [
                {
                    "term": "投資",
                    "reading": "とうし",
                    "english": "investment",
                    "definition": "利益を得るために資金を投じること"
                },
                {
                    "term": "利益",
                    "reading": "りえき",
                    "english": "profit",
                    "definition": "収入から費用を引いた額"
                },
                {
                    "term": "損失",
                    "reading": "そんしつ",
                    "english": "loss",
                    "definition": "失った金額"
                },
                {
                    "term": "資産",
                    "reading": "しさん",
                    "english": "assets",
                    "definition": "所有する財産"
                },
                {
                    "term": "負債",
                    "reading": "ふさい",
                    "english": "liability",
                    "definition": "返済義務のある借金"
                },
                {
                    "term": "株式",
                    "reading": "かぶしき",
                    "english": "stock",
                    "definition": "会社の所有権の一部"
                },
                {
                    "term": "債券",
                    "reading": "さいけん",
                    "english": "bond",
                    "definition": "借金の証書"
                },
                {
                    "term": "為替",
                    "reading": "かわせ",
                    "english": "exchange",
                    "definition": "通貨の交換"
                },
                {
                    "term": "金利",
                    "reading": "きんり",
                    "english": "interest rate",
                    "definition": "お金を借りる際の利率"
                },
                {
                    "term": "配当",
                    "reading": "はいとう",
                    "english": "dividend",
                    "definition": "株主への利益分配"
                }
            ]
        }
    
    @staticmethod
    def get_augmented_seasonal_expression_examples() -> Dict[str, List[Dict]]:
        """拡張された季節の表現例を取得"""
        return {
            "spring": [
                {
                    "expression": "桜が満開です",
                    "reading": "さくらがまんかいです",
                    "context": "桜の季節",
                    "usage": "春の美しさを表現"
                },
                {
                    "expression": "春の陽気",
                    "reading": "はるのようき",
                    "context": "暖かい天気",
                    "usage": "春の暖かさを表現"
                },
                {
                    "expression": "花見",
                    "reading": "はなみ",
                    "context": "桜を見る行事",
                    "usage": "春の行事"
                },
                {
                    "expression": "新緑の季節",
                    "reading": "しんりょくのきせつ",
                    "context": "若葉の時期",
                    "usage": "初夏の表現"
                },
                {
                    "expression": "春眠暁を覚えず",
                    "reading": "しゅんみんあかつきをおぼえず",
                    "context": "春の朝寝坊",
                    "usage": "春の慣用句"
                },
                {
                    "expression": "菜の花畑",
                    "reading": "なのはなばたけ",
                    "context": "春の風景",
                    "usage": "春の田園風景"
                },
                {
                    "expression": "雪解け",
                    "reading": "ゆきどけ",
                    "context": "春の訪れ",
                    "usage": "冬から春への変化"
                },
                {
                    "expression": "うららかな春の日",
                    "reading": "うららかなはるのひ",
                    "context": "穏やかな春日和",
                    "usage": "春の気候描写"
                }
            ],
            "summer": [
                {
                    "expression": "蒸し暑い",
                    "reading": "むしあつい",
                    "context": "夏の湿度",
                    "usage": "夏の不快な暑さ"
                },
                {
                    "expression": "猛暑",
                    "reading": "もうしょ",
                    "context": "激しい暑さ",
                    "usage": "極端な暑さ"
                },
                {
                    "expression": "夏祭り",
                    "reading": "なつまつり",
                    "context": "夏の行事",
                    "usage": "夏の風物詩"
                },
                {
                    "expression": "花火大会",
                    "reading": "はなびたいかい",
                    "context": "夏の夜のイベント",
                    "usage": "夏の行事"
                },
                {
                    "expression": "蝉の声",
                    "reading": "せみのこえ",
                    "context": "夏の音",
                    "usage": "夏の風物詩"
                },
                {
                    "expression": "涼を求める",
                    "reading": "りょうをもとめる",
                    "context": "暑さ対策",
                    "usage": "涼しさを探す"
                },
                {
                    "expression": "夕涼み",
                    "reading": "ゆうすずみ",
                    "context": "夕方の涼しさ",
                    "usage": "夏の夕方の過ごし方"
                },
                {
                    "expression": "風鈴",
                    "reading": "ふうりん",
                    "context": "夏の音",
                    "usage": "涼を感じる道具"
                }
            ],
            "autumn": [
                {
                    "expression": "紅葉狩り",
                    "reading": "もみじがり",
                    "context": "紅葉見物",
                    "usage": "秋の行事"
                },
                {
                    "expression": "秋の夜長",
                    "reading": "あきのよなが",
                    "context": "長い夜",
                    "usage": "秋の特徴"
                },
                {
                    "expression": "実りの秋",
                    "reading": "みのりのあき",
                    "context": "収穫の季節",
                    "usage": "豊作を表現"
                },
                {
                    "expression": "食欲の秋",
                    "reading": "しょくよくのあき",
                    "context": "食べ物が美味しい季節",
                    "usage": "秋の特徴"
                },
                {
                    "expression": "読書の秋",
                    "reading": "どくしょのあき",
                    "context": "読書に適した季節",
                    "usage": "秋の過ごし方"
                },
                {
                    "expression": "秋晴れ",
                    "reading": "あきばれ",
                    "context": "秋の晴天",
                    "usage": "秋の気候"
                },
                {
                    "expression": "月見",
                    "reading": "つきみ",
                    "context": "中秋の名月",
                    "usage": "秋の行事"
                },
                {
                    "expression": "枯葉",
                    "reading": "かれは",
                    "context": "落ち葉",
                    "usage": "秋から冬への変化"
                }
            ],
            "winter": [
                {
                    "expression": "雪景色",
                    "reading": "ゆきげしき",
                    "context": "雪の風景",
                    "usage": "冬の美しさ"
                },
                {
                    "expression": "寒さが身にしみる",
                    "reading": "さむさがみにしみる",
                    "context": "厳しい寒さ",
                    "usage": "寒さの表現"
                },
                {
                    "expression": "こたつ",
                    "reading": "こたつ",
                    "context": "暖房器具",
                    "usage": "冬の生活"
                },
                {
                    "expression": "年末年始",
                    "reading": "ねんまつねんし",
                    "context": "年の変わり目",
                    "usage": "冬の行事"
                },
                {
                    "expression": "初詣",
                    "reading": "はつもうで",
                    "context": "新年の参拝",
                    "usage": "正月行事"
                },
                {
                    "expression": "雪だるま",
                    "reading": "ゆきだるま",
                    "context": "雪遊び",
                    "usage": "冬の遊び"
                },
                {
                    "expression": "北風",
                    "reading": "きたかぜ",
                    "context": "冬の風",
                    "usage": "寒さの原因"
                },
                {
                    "expression": "春待ち",
                    "reading": "はるまち",
                    "context": "春を待つ気持ち",
                    "usage": "冬の終わり"
                }
            ]
        }
    
    @staticmethod
    def get_augmented_social_context_examples() -> Dict[str, List[Dict]]:
        """拡張された社会的文脈の例を取得"""
        return {
            "gift_giving": [
                {
                    "occasion": "お中元",
                    "phrase": "心ばかりの品ですが",
                    "meaning": "ささやかな贈り物の謙遜表現",
                    "response": "ありがとうございます。お気遣いいただいて"
                },
                {
                    "occasion": "お歳暮",
                    "phrase": "今年もお世話になりました",
                    "meaning": "年末の感謝の挨拶",
                    "response": "こちらこそ、ありがとうございました"
                },
                {
                    "occasion": "結婚祝い",
                    "phrase": "末永くお幸せに",
                    "meaning": "新婚夫婦への祝福",
                    "response": "温かいお祝いをありがとうございます"
                },
                {
                    "occasion": "出産祝い",
                    "phrase": "健やかな成長をお祈りしています",
                    "meaning": "赤ちゃんへの祝福",
                    "response": "ありがとうございます。大切に使わせていただきます"
                },
                {
                    "occasion": "引越し祝い",
                    "phrase": "新生活が素晴らしいものになりますように",
                    "meaning": "新居への祝福",
                    "response": "お心遣いありがとうございます"
                },
                {
                    "occasion": "快気祝い",
                    "phrase": "お陰様で元気になりました",
                    "meaning": "病気回復の報告と感謝",
                    "response": "お元気になられて何よりです"
                }
            ],
            "visiting": [
                {
                    "situation": "訪問時",
                    "phrase": "お邪魔します",
                    "meaning": "家に入る時の挨拶",
                    "response": "どうぞお上がりください"
                },
                {
                    "situation": "長居した後",
                    "phrase": "そろそろ失礼します",
                    "meaning": "帰る意思を伝える",
                    "response": "もう少しゆっくりしていってください"
                },
                {
                    "situation": "手土産を渡す時",
                    "phrase": "つまらないものですが",
                    "meaning": "謙遜しながら贈り物を渡す",
                    "response": "お気遣いなく"
                },
                {
                    "situation": "お茶を出された時",
                    "phrase": "いただきます",
                    "meaning": "飲食前の挨拶",
                    "response": "どうぞ召し上がってください"
                },
                {
                    "situation": "帰り際",
                    "phrase": "今日はありがとうございました",
                    "meaning": "訪問の感謝",
                    "response": "こちらこそ、楽しかったです"
                }
            ],
            "dining": [
                {
                    "situation": "食事の開始",
                    "phrase": "いただきます",
                    "meaning": "食事前の挨拶",
                    "cultural_note": "作った人と食材への感謝"
                },
                {
                    "situation": "食事の終了",
                    "phrase": "ごちそうさまでした",
                    "meaning": "食事後の挨拶",
                    "cultural_note": "感謝の表現"
                },
                {
                    "situation": "お箸の使い方",
                    "correct": "箸置きに置く",
                    "incorrect": "ご飯に刺す（仏箸）",
                    "cultural_note": "葬儀を連想させるため避ける"
                },
                {
                    "situation": "おかわり",
                    "phrase": "もう少しいただいてもよろしいですか",
                    "meaning": "おかわりを頼む",
                    "response": "どうぞ遠慮なく"
                },
                {
                    "situation": "苦手な食べ物",
                    "phrase": "申し訳ありませんが、これは少し苦手で",
                    "meaning": "丁寧に断る",
                    "response": "無理なさらないでください"
                }
            ],
            "workplace": [
                {
                    "situation": "出社時",
                    "phrase": "おはようございます",
                    "meaning": "朝の挨拶（時間に関係なく）",
                    "note": "職場では一日中使える"
                },
                {
                    "situation": "退社時",
                    "phrase": "お先に失礼します",
                    "meaning": "先に帰る時の挨拶",
                    "response": "お疲れ様でした"
                },
                {
                    "situation": "外出時",
                    "phrase": "行ってきます",
                    "meaning": "一時的に職場を離れる",
                    "response": "行ってらっしゃい"
                },
                {
                    "situation": "帰社時",
                    "phrase": "ただいま戻りました",
                    "meaning": "外出から戻った時",
                    "response": "お帰りなさい"
                },
                {
                    "situation": "休憩時",
                    "phrase": "少し休憩させていただきます",
                    "meaning": "休憩を取る許可",
                    "response": "どうぞ"
                }
            ]
        }
    
    @staticmethod
    def get_augmented_regional_dialect_examples() -> Dict[str, List[Dict]]:
        """拡張された方言の例を取得"""
        return {
            "kansai": [
                {"standard": "違う", "dialect": "ちゃう", "meaning": "different"},
                {"standard": "とても", "dialect": "めっちゃ", "meaning": "very"},
                {"standard": "だから", "dialect": "せやから", "meaning": "therefore"},
                {"standard": "本当", "dialect": "ほんま", "meaning": "really"},
                {"standard": "できない", "dialect": "でけへん", "meaning": "cannot"},
                {"standard": "いらない", "dialect": "いらん", "meaning": "don't need"},
                {"standard": "知らない", "dialect": "知らん", "meaning": "don't know"},
                {"standard": "行かない", "dialect": "行かへん", "meaning": "won't go"},
                {"standard": "ダメ", "dialect": "あかん", "meaning": "no good"},
                {"standard": "しんどい", "dialect": "しんどい", "meaning": "tired"},
                {"standard": "捨てる", "dialect": "ほかす", "meaning": "throw away"},
                {"standard": "買う", "dialect": "こうた", "meaning": "bought"},
                {"standard": "ありがとう", "dialect": "おおきに", "meaning": "thank you"},
                {"standard": "そうですね", "dialect": "せやな", "meaning": "that's right"},
                {"standard": "何してるの？", "dialect": "何してんの？", "meaning": "what are you doing?"}
            ],
            "tohoku": [
                {"standard": "寒い", "dialect": "しばれる", "meaning": "cold"},
                {"standard": "そうだ", "dialect": "んだ", "meaning": "that's right"},
                {"standard": "違う", "dialect": "違ぐ", "meaning": "different"},
                {"standard": "行く", "dialect": "行ぐ", "meaning": "go"},
                {"standard": "だけど", "dialect": "だげんと", "meaning": "but"},
                {"standard": "どうして", "dialect": "なして", "meaning": "why"},
                {"standard": "大丈夫", "dialect": "大丈夫だ", "meaning": "okay"},
                {"standard": "疲れた", "dialect": "こわい", "meaning": "tired"},
                {"standard": "たくさん", "dialect": "いっぺ", "meaning": "a lot"},
                {"standard": "ください", "dialect": "けろ", "meaning": "please give"}
            ],
            "hakata": [
                {"standard": "とても", "dialect": "ばり", "meaning": "very"},
                {"standard": "何？", "dialect": "なん？", "meaning": "what?"},
                {"standard": "そうだよ", "dialect": "そうたい", "meaning": "that's right"},
                {"standard": "いいよ", "dialect": "よかよ", "meaning": "it's fine"},
                {"standard": "好き", "dialect": "好いとう", "meaning": "like"},
                {"standard": "だから", "dialect": "やけん", "meaning": "so"},
                {"standard": "しなさい", "dialect": "しんしゃい", "meaning": "do it"},
                {"standard": "どうしたの？", "dialect": "どげんしたと？", "meaning": "what happened?"},
                {"standard": "行こう", "dialect": "行こうや", "meaning": "let's go"},
                {"standard": "違う", "dialect": "違うっちゃ", "meaning": "it's different"}
            ],
            "okinawa": [
                {"standard": "こんにちは", "dialect": "はいさい", "meaning": "hello (male)"},
                {"standard": "こんにちは", "dialect": "はいたい", "meaning": "hello (female)"},
                {"standard": "ありがとう", "dialect": "にふぇーでーびる", "meaning": "thank you"},
                {"standard": "頑張って", "dialect": "ちばりよー", "meaning": "good luck"},
                {"standard": "美味しい", "dialect": "まーさん", "meaning": "delicious"},
                {"standard": "大きい", "dialect": "まぎー", "meaning": "big"},
                {"standard": "小さい", "dialect": "ぐなさん", "meaning": "small"},
                {"standard": "暑い", "dialect": "あちさん", "meaning": "hot"},
                {"standard": "寒い", "dialect": "ひーさん", "meaning": "cold"},
                {"standard": "楽しい", "dialect": "ちむどんどん", "meaning": "exciting"}
            ],
            "hiroshima": [
                {"standard": "とても", "dialect": "ぶち", "meaning": "very"},
                {"standard": "だから", "dialect": "じゃけん", "meaning": "therefore"},
                {"standard": "そうだ", "dialect": "そうじゃ", "meaning": "that's right"},
                {"standard": "ダメ", "dialect": "いけん", "meaning": "no good"},
                {"standard": "しなさい", "dialect": "しんさい", "meaning": "do it"},
                {"standard": "ありがとう", "dialect": "ありがとうの", "meaning": "thank you"},
                {"standard": "すごい", "dialect": "たいぎい", "meaning": "amazing"},
                {"standard": "疲れた", "dialect": "えらい", "meaning": "tired"},
                {"standard": "行く", "dialect": "行くけぇ", "meaning": "will go"},
                {"standard": "食べる", "dialect": "食べるんよ", "meaning": "will eat"}
            ]
        }
    
    @staticmethod
    def get_augmented_age_gender_language_examples() -> Dict[str, List[Dict]]:
        """拡張された年齢・性別言語の例を取得"""
        return {
            "feminine": [
                {
                    "expression": "〜かしら",
                    "example": "明日は晴れるかしら",
                    "meaning": "I wonder if it will be sunny tomorrow",
                    "formality": "casual"
                },
                {
                    "expression": "〜わ",
                    "example": "きれいだわ",
                    "meaning": "It's beautiful",
                    "formality": "casual"
                },
                {
                    "expression": "〜のよ",
                    "example": "知らないのよ",
                    "meaning": "I don't know",
                    "formality": "casual"
                },
                {
                    "expression": "あら",
                    "example": "あら、そうなの？",
                    "meaning": "Oh, is that so?",
                    "formality": "casual"
                },
                {
                    "expression": "まあ",
                    "example": "まあ、素敵！",
                    "meaning": "Oh, how wonderful!",
                    "formality": "casual"
                },
                {
                    "expression": "〜ですこと",
                    "example": "お上手ですこと",
                    "meaning": "How skillful you are",
                    "formality": "formal"
                },
                {
                    "expression": "〜ですもの",
                    "example": "知らないんですもの",
                    "meaning": "Because I don't know",
                    "formality": "casual"
                },
                {
                    "expression": "お〜になる",
                    "example": "お帰りになる",
                    "meaning": "to return (honorific)",
                    "formality": "formal"
                }
            ],
            "masculine": [
                {
                    "expression": "〜ぞ",
                    "example": "行くぞ",
                    "meaning": "Let's go!",
                    "formality": "casual"
                },
                {
                    "expression": "〜ぜ",
                    "example": "頑張るぜ",
                    "meaning": "I'll do my best!",
                    "formality": "casual"
                },
                {
                    "expression": "おい",
                    "example": "おい、待てよ",
                    "meaning": "Hey, wait!",
                    "formality": "casual"
                },
                {
                    "expression": "俺",
                    "example": "俺が行く",
                    "meaning": "I (masculine) will go",
                    "formality": "casual"
                },
                {
                    "expression": "〜だろ",
                    "example": "そうだろ？",
                    "meaning": "Right?",
                    "formality": "casual"
                },
                {
                    "expression": "〜じゃねえ",
                    "example": "違うじゃねえか",
                    "meaning": "That's not right!",
                    "formality": "very casual"
                },
                {
                    "expression": "〜ってば",
                    "example": "聞いてるってば",
                    "meaning": "I'm listening!",
                    "formality": "casual"
                },
                {
                    "expression": "〜んだよ",
                    "example": "知らないんだよ",
                    "meaning": "I don't know",
                    "formality": "casual"
                }
            ],
            "youth": [
                {
                    "expression": "マジで",
                    "example": "マジで？すごい！",
                    "meaning": "Really? Amazing!",
                    "age_group": "teens-20s"
                },
                {
                    "expression": "ヤバい",
                    "example": "この料理ヤバい（美味しい）",
                    "meaning": "This food is amazing",
                    "age_group": "teens-20s"
                },
                {
                    "expression": "ウケる",
                    "example": "それウケる！",
                    "meaning": "That's hilarious!",
                    "age_group": "teens-20s"
                },
                {
                    "expression": "めっちゃ",
                    "example": "めっちゃ楽しい",
                    "meaning": "Super fun",
                    "age_group": "teens-30s"
                },
                {
                    "expression": "ガチで",
                    "example": "ガチで頑張る",
                    "meaning": "Seriously trying hard",
                    "age_group": "teens-20s"
                },
                {
                    "expression": "ビミョー",
                    "example": "味がビミョー",
                    "meaning": "The taste is so-so",
                    "age_group": "teens-30s"
                },
                {
                    "expression": "ググる",
                    "example": "分からないからググる",
                    "meaning": "I'll Google it",
                    "age_group": "all ages"
                },
                {
                    "expression": "エモい",
                    "example": "この曲エモい",
                    "meaning": "This song is emotional",
                    "age_group": "teens-20s"
                },
                {
                    "expression": "ワンチャン",
                    "example": "ワンチャンある",
                    "meaning": "There's a chance",
                    "age_group": "teens-20s"
                },
                {
                    "expression": "それな",
                    "example": "A: 疲れた B: それな",
                    "meaning": "I agree / Same here",
                    "age_group": "teens-20s"
                }
            ],
            "elderly": [
                {
                    "expression": "〜じゃ",
                    "example": "そうじゃのう",
                    "meaning": "I see",
                    "age_group": "60+"
                },
                {
                    "expression": "わし",
                    "example": "わしが若い頃は",
                    "meaning": "When I was young",
                    "age_group": "elderly male"
                },
                {
                    "expression": "〜のう",
                    "example": "暖かいのう",
                    "meaning": "It's warm, isn't it",
                    "age_group": "60+"
                },
                {
                    "expression": "〜じゃて",
                    "example": "聞いたことがあるじゃて",
                    "meaning": "I've heard that",
                    "age_group": "elderly"
                },
                {
                    "expression": "あんた",
                    "example": "あんた、元気かい",
                    "meaning": "Are you well?",
                    "age_group": "elderly"
                },
                {
                    "expression": "〜かのう",
                    "example": "できるかのう",
                    "meaning": "I wonder if I can",
                    "age_group": "elderly"
                },
                {
                    "expression": "ご苦労さん",
                    "example": "今日もご苦労さん",
                    "meaning": "Thank you for your hard work",
                    "age_group": "elderly"
                },
                {
                    "expression": "まあまあ",
                    "example": "まあまあ、落ち着いて",
                    "meaning": "Now, now, calm down",
                    "age_group": "middle-aged+"
                }
            ]
        }
    
    @staticmethod
    def get_augmented_emotional_expression_examples() -> Dict[str, List[Dict]]:
        """拡張された感情表現の例を取得"""
        return {
            "happiness": [
                {
                    "level": "slight",
                    "expression": "嬉しい",
                    "context": "プレゼントをもらった",
                    "example": "プレゼントありがとう、嬉しい！"
                },
                {
                    "level": "moderate",
                    "expression": "とても嬉しい",
                    "context": "試験に合格した",
                    "example": "合格できて、とても嬉しいです"
                },
                {
                    "level": "extreme",
                    "expression": "嬉しくて涙が出そう",
                    "context": "夢が叶った",
                    "example": "夢が叶って、嬉しくて涙が出そうです"
                },
                {
                    "level": "ecstatic",
                    "expression": "天にも昇る気持ち",
                    "context": "結婚が決まった",
                    "example": "結婚が決まって、天にも昇る気持ちです"
                }
            ],
            "sadness": [
                {
                    "level": "slight",
                    "expression": "ちょっと寂しい",
                    "context": "友達が引っ越す",
                    "example": "友達が引っ越すから、ちょっと寂しい"
                },
                {
                    "level": "moderate",
                    "expression": "悲しい",
                    "context": "ペットが亡くなった",
                    "example": "ペットが亡くなって、とても悲しい"
                },
                {
                    "level": "deep",
                    "expression": "胸が張り裂けそう",
                    "context": "大切な人との別れ",
                    "example": "別れが辛くて、胸が張り裂けそうです"
                },
                {
                    "level": "overwhelming",
                    "expression": "涙が止まらない",
                    "context": "感動的な出来事",
                    "example": "あまりに感動して、涙が止まりません"
                }
            ],
            "anger": [
                {
                    "level": "mild",
                    "expression": "ちょっとイライラする",
                    "context": "電車が遅れた",
                    "example": "また電車が遅れて、ちょっとイライラする"
                },
                {
                    "level": "moderate",
                    "expression": "腹が立つ",
                    "context": "約束を破られた",
                    "example": "約束を破られて、本当に腹が立つ"
                },
                {
                    "level": "strong",
                    "expression": "頭にくる",
                    "context": "嘘をつかれた",
                    "example": "嘘をつかれて、すごく頭にきた"
                },
                {
                    "level": "extreme",
                    "expression": "怒りで震える",
                    "context": "ひどい扱いを受けた",
                    "example": "あまりのひどさに、怒りで震えました"
                }
            ],
            "fear": [
                {
                    "level": "slight",
                    "expression": "ちょっと怖い",
                    "context": "暗い道を歩く",
                    "example": "夜の暗い道は、ちょっと怖い"
                },
                {
                    "level": "moderate",
                    "expression": "怖くて足がすくむ",
                    "context": "高所恐怖症",
                    "example": "高い所は怖くて足がすくみます"
                },
                {
                    "level": "intense",
                    "expression": "恐怖で凍りつく",
                    "context": "危険な状況",
                    "example": "突然の出来事に、恐怖で凍りつきました"
                },
                {
                    "level": "panic",
                    "expression": "パニックになる",
                    "context": "緊急事態",
                    "example": "地震でパニックになってしまった"
                }
            ],
            "surprise": [
                {
                    "level": "mild",
                    "expression": "あら、びっくり",
                    "context": "偶然の出会い",
                    "example": "あら、こんなところで会うなんてびっくり"
                },
                {
                    "level": "moderate",
                    "expression": "驚いた",
                    "context": "予想外の結果",
                    "example": "まさか優勝するなんて、本当に驚いた"
                },
                {
                    "level": "extreme",
                    "expression": "言葉を失う",
                    "context": "衝撃的なニュース",
                    "example": "あまりの衝撃に言葉を失いました"
                },
                {
                    "level": "shock",
                    "expression": "腰を抜かす",
                    "context": "信じられない出来事",
                    "example": "信じられなくて腰を抜かしそうになった"
                }
            ]
        }
    
def augment_advanced_task_classes():
    """
    高度なタスククラスのサンプルデータを増幅する処理
    実際の実装時にこの関数を呼び出してタスククラスを更新
    """
    augmenter = AdvancedTaskSampleAugmenter()
    
    # 各メソッドから増幅されたデータを取得
    augmented_data = {
        'onomatopoeia': augmenter.get_augmented_onomatopoeia_examples(),
        'conversation': augmenter.get_augmented_conversation_examples(),
        'proverb_idiom': augmenter.get_augmented_proverb_idiom_examples(),
        'business_japanese': augmenter.get_augmented_business_japanese_examples(),
        'classical_japanese': augmenter.get_augmented_classical_japanese_examples(),
        'specialized_vocabulary': augmenter.get_augmented_specialized_vocabulary_examples(),
        'seasonal_expression': augmenter.get_augmented_seasonal_expression_examples(),
        'social_context': augmenter.get_augmented_social_context_examples(),
        'regional_dialect': augmenter.get_augmented_regional_dialect_examples(),
        'age_gender_language': augmenter.get_augmented_age_gender_language_examples(),
        'emotional_expression': augmenter.get_augmented_emotional_expression_examples()
    }
    
    return augmented_data