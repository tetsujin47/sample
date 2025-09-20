"""Static resources for conversation scenarios and the phrasebook."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence, Tuple


@dataclass(frozen=True)
class ConversationTurn:
    prompt: str
    keywords: Sequence[str] = field(default_factory=list)
    hints: Sequence[str] = field(default_factory=list)
    sample_response: str = ""
    grammar_focus: str = ""


@dataclass(frozen=True)
class Scenario:
    id: str
    title: str
    description: str
    partner_role: str
    goals: Sequence[str]
    turns: Sequence[ConversationTurn]
    tips: Sequence[str]
    phrasebook: Sequence[Tuple[str, str]] = field(default_factory=list)


SCENARIOS: List[Scenario] = [
    Scenario(
        id="coffee-shop",
        title="Coffee Shop",
        description=(
            "You are ordering a drink at a cosy cafe during the morning rush."
        ),
        partner_role="Barista",
        goals=(
            "Order a drink clearly.",
            "Handle follow-up questions politely.",
            "Confirm your order before paying.",
        ),
        turns=[
            ConversationTurn(
                prompt="Good morning! What can I get started for you today?",
                keywords=(
                    "latte",
                    "coffee",
                    "tea",
                    "americano",
                    "cappuccino",
                ),
                hints=(
                    "注文したい飲み物をはっきり伝えましょう。",
                    "例: I'd like a latte, please.",
                ),
                sample_response="I'd like a vanilla latte, please.",
                grammar_focus="注文には 'I'd like ...' が便利です。",
            ),
            ConversationTurn(
                prompt="Would you like that hot or iced?",
                keywords=("hot", "iced", "either"),
                hints=("温かいか冷たいかを選びましょう。",),
                sample_response="Iced, please.",
                grammar_focus="形容詞を使って注文の詳細を伝える練習です。",
            ),
            ConversationTurn(
                prompt="Do you want any pastries today?",
                keywords=("yes", "no", "croissant", "muffin"),
                hints=("欲しいものがあれば追加で注文しましょう。",),
                sample_response="No thanks, just the latte.",
                grammar_focus="丁寧に断る表現 'No thanks, ...' を使ってみましょう。",
            ),
        ],
        tips=(
            "注文する前に飲み物のサイズを考えておきましょう。",
            "聞き返す時は 'Could you repeat that, please?' を使いましょう。",
        ),
        phrasebook=(
            ("I'd like a [drink], please.", "[飲み物]をお願いします。"),
            ("Can I have it iced?", "アイスにできますか？"),
            ("That's all, thank you.", "以上です、ありがとうございます。"),
        ),
    ),
    Scenario(
        id="hotel-check-in",
        title="Hotel Check-in",
        description="You arrive at the front desk of your hotel in the evening.",
        partner_role="Receptionist",
        goals=(
            "Confirm your reservation details.",
            "Make a simple request during check-in.",
            "Respond naturally to polite questions.",
        ),
        turns=[
            ConversationTurn(
                prompt="Good evening, welcome to Brightview Hotel. Do you have a reservation?",
                keywords=("yes", "reservation", "booking"),
                hints=("予約済みならそのことを伝えましょう。",),
                sample_response="Yes, I booked a room under the name Sato.",
                grammar_focus="予約について話す時は 'booked a room' を使います。",
            ),
            ConversationTurn(
                prompt="May I see your passport, please?",
                keywords=("here", "passport", "sure"),
                hints=("差し出す時は 'Here you go.' が自然です。",),
                sample_response="Of course, here you are.",
                grammar_focus="丁寧に手渡す表現 'Here you are.' を使いましょう。",
            ),
            ConversationTurn(
                prompt="Would you like a wake-up call for tomorrow morning?",
                keywords=("yes", "no", "please"),
                hints=("必要であれば希望の時間を伝えましょう。",),
                sample_response="Yes, please. Could you call me at 6:30 a.m.?",
                grammar_focus="希望を伝える丁寧な依頼文を練習しましょう。",
            ),
        ],
        tips=(
            "宿泊に関する質問に 'Absolutely' や 'Not at the moment' などで答えると自然です。",
            "特別な希望があれば遠慮せずに伝えましょう。",
        ),
        phrasebook=(
            ("I have a reservation under [name].", "[名前]で予約しています。"),
            ("Could I have a wake-up call at [time]?", "[時間]にモーニングコールをお願いできますか。"),
            ("Is breakfast included?", "朝食は含まれていますか？"),
        ),
    ),
    Scenario(
        id="job-interview",
        title="Job Interview",
        description="You are interviewing for a junior marketing position.",
        partner_role="Interviewer",
        goals=(
            "Introduce yourself professionally.",
            "Describe a past experience confidently.",
            "Ask a thoughtful question at the end.",
        ),
        turns=[
            ConversationTurn(
                prompt="Thanks for coming in today. Could you start by introducing yourself?",
                keywords=("name", "experience", "student", "marketing"),
                hints=("名前、経験、興味を簡潔にまとめましょう。",),
                sample_response=(
                    "My name is Keiko, and I recently graduated with a degree in marketing."
                ),
                grammar_focus="自己紹介では 'My name is ...' から始めましょう。",
            ),
            ConversationTurn(
                prompt="Can you tell me about a project you're proud of?",
                keywords=("project", "campaign", "team", "results"),
                hints=("STAR 法で説明するとわかりやすくなります。",),
                sample_response=(
                    "I led a social media campaign at university that increased engagement by 30%."
                ),
                grammar_focus="過去の経験を語るときは過去形を使いましょう。",
            ),
            ConversationTurn(
                prompt="Do you have any questions for us?",
                keywords=("ask", "question", "role", "team"),
                hints=("ポジティブな質問を用意しておくと好印象です。",),
                sample_response="Yes, could you tell me more about the team I'll be working with?",
                grammar_focus="面接の最後には感謝を伝えることも忘れずに。",
            ),
        ],
        tips=(
            "具体例を挙げながら答えると説得力が増します。",
            "面接官の質問を復唱することで時間を稼げます。",
        ),
        phrasebook=(
            ("I have experience in [area].", "[分野]での経験があります。"),
            ("One of my strengths is [skill].", "私の強みは[スキル]です。"),
            ("Thank you for the opportunity today.", "本日は機会をいただきありがとうございます。"),
        ),
    ),
]


def get_phrasebook_sections() -> List[Tuple[str, Sequence[Tuple[str, str]]]]:
    """Group phrasebook entries by scenario title for quick lookup."""

    return [(scenario.title, scenario.phrasebook) for scenario in SCENARIOS]

