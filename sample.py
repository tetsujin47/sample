
"""Command line English conversation practice application.

This module defines a small interactive programme that helps learners
practise English conversation.  The application offers ready-made
scenarios, a phrasebook, a simple response generator and keeps track of
previous practice sessions.  It is intentionally designed to run in a
terminal so that it can work in an offline coding exercise environment.

Run the application without arguments to enter the interactive mode::

    python sample.py

If you simply want to preview the experience without interacting, pass
``--demo`` to automatically play through the first scenario using model
responses::

    python sample.py --demo

The module can also serve as an example of structuring a moderately
complex command line application in Python without external
dependencies.
"""

from __future__ import annotations

import argparse
import random
import textwrap
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


@dataclass
class ConversationTurn:
    """A single exchange within a scenario.

    Attributes
    ----------
    prompt:
        The line delivered by the conversation partner.
    keywords:
        Lower-case keywords that are expected from the learner's
        response.  A response is considered successful if at least one
        keyword appears.
    hints:
        Optional hints or translations that support the learner.  The
        user can ask for these during the conversation by typing
        ``?hint``.
    sample_response:
        A model answer that the learner can view with ``?sample``.
    grammar_focus:
        A short explanation of the expression or grammar point that the
        turn emphasises.
    """

    prompt: str
    keywords: Sequence[str]
    hints: Sequence[str] = field(default_factory=list)
    sample_response: str = ""
    grammar_focus: str = ""


@dataclass
class Scenario:
    """A conversation scenario with several turns."""

    title: str
    description: str
    partner_role: str
    turns: Sequence[ConversationTurn]
    tips: Sequence[str]
    phrasebook: Sequence[Tuple[str, str]] = field(default_factory=list)


class EnglishConversationApp:
    """Command line English conversation practice application."""

    def __init__(self) -> None:
        self.scenarios: List[Scenario] = self._load_scenarios()
        self.history: List[Dict[str, object]] = []
        self.phrasebook: Dict[str, List[Tuple[str, str]]] = (
            self._build_phrasebook()
        )
        self.response_templates: Dict[str, List[str]] = self._load_templates()
        self._wrapper = textwrap.TextWrapper(width=72)

    # ------------------------------------------------------------------
    # Scenario and resource definitions
    # ------------------------------------------------------------------
    def _load_scenarios(self) -> List[Scenario]:
        """Create the list of built-in conversation scenarios."""

        return [
            Scenario(
                title="Coffee Shop",
                description=(
                    "You are ordering a drink at a cosy cafe during the "
                    "morning rush."
                ),
                partner_role="Barista",
                turns=[
                    ConversationTurn(
                        prompt=(
                            "Good morning! What can I get started for you "
                            "today?"
                        ),
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
                        hints=(
                            "温かいか冷たいかを選ぶ質問です。",
                            "hot = 温かい, iced = 氷入り",
                        ),
                        sample_response="Could I have it iced, please?",
                        grammar_focus="質問に合わせて形容詞で答える練習です。",
                    ),
                    ConversationTurn(
                        prompt="Anything else for you today?",
                        keywords=("that's all", "that's it", "just", "no"),
                        hints=(
                            "追加注文が必要か聞かれています。",
                            """that's all = 以上です""",
                        ),
                        sample_response="No, that's all for now, thank you.",
                        grammar_focus="丁寧に断る表現。",
                    ),
                    ConversationTurn(
                        prompt="Great! Can I have your name for the order?",
                        keywords=("it's", "my name", "call me"),
                        hints=(
                            "名前を伝えるフレーズを使ってみましょう。",
                            "例: It's Ken.",
                        ),
                        sample_response="Sure, it's Aya.",
                        grammar_focus="自己紹介に使える 'It's ...' の形。",
                    ),
                ],
                tips=(
                    "注文するときは 'I'd like ...' や 'Could I have ...' を使いましょう。",
                    "最後にお礼を伝えると丁寧な印象になります。",
                ),
                phrasebook=(
                    ("I'd like a latte, please.", "ラテをお願いします。"),
                    ("Could you make that decaf?", "デカフェにしていただけますか。"),
                    ("That's all for now, thanks.", "以上でお願いします。"),
                    ("Can I have it to go?", "持ち帰りでお願いします。"),
                ),
            ),
            Scenario(
                title="New Coworker",
                description=(
                    "You are meeting a new coworker on your first day at "
                    "the office."
                ),
                partner_role="Coworker",
                turns=[
                    ConversationTurn(
                        prompt="Hi, I'm Sarah from marketing. Are you new here?",
                        keywords=("nice", "meet", "yes", "first day"),
                        hints=(
                            "挨拶と自己紹介の表現を組み合わせましょう。",
                            "例: Yes, I'm new here. Nice to meet you!",
                        ),
                        sample_response=(
                            "Yes, I just joined the product team. Nice to meet you!"
                        ),
                        grammar_focus="自己紹介と挨拶の組み合わせ。",
                    ),
                    ConversationTurn(
                        prompt="What kind of projects will you be working on?",
                        keywords=("project", "working", "app", "service", "plan"),
                        hints=(
                            "担当予定の仕事を簡単に説明しましょう。",
                            "project = プロジェクト、取り組み",
                        ),
                        sample_response=(
                            "I'll be working on our mobile app redesign and some user interviews."
                        ),
                        grammar_focus="未来の予定には 'will' や 'be going to'。",
                    ),
                    ConversationTurn(
                        prompt="Let me know if you need any help settling in.",
                        keywords=("thank", "appreciate", "that's kind"),
                        hints=(
                            "助けの申し出には感謝を伝えます。",
                            "thank you so much = とてもありがとう",
                        ),
                        sample_response="Thank you, I really appreciate it!",
                        grammar_focus="感謝を伝える表現。",
                    ),
                    ConversationTurn(
                        prompt="Do you want to grab lunch together sometime?",
                        keywords=("sure", "love", "sounds", "great"),
                        hints=(
                            "誘いには肯定的に答えてみましょう。",
                            "例: That sounds great!",
                        ),
                        sample_response="That sounds great. I'd love to!",
                        grammar_focus="誘いに応じる表現。",
                    ),
                ],
                tips=(
                    "自己紹介では笑顔と挨拶を忘れずに。",
                    "質問で会話を続けると、距離が縮まります。",
                ),
                phrasebook=(
                    ("Nice to meet you!", "お会いできて嬉しいです。"),
                    ("I just joined the team this week.", "今週チームに加わったばかりです。"),
                    ("Thanks, I appreciate your help.", "ありがとうございます、助かります。"),
                    ("Let's have lunch together soon.", "近いうちに一緒にランチしましょう。"),
                ),
            ),
            Scenario(
                title="Asking for Directions",
                description=(
                    "You are travelling in a new city and ask a friendly "
                    "local for directions."
                ),
                partner_role="Local resident",
                turns=[
                    ConversationTurn(
                        prompt=(
                            "Hi there, you look a little lost. Where are you "
                            "trying to go?"
                        ),
                        keywords=("station", "museum", "hotel", "downtown", "airport"),
                        hints=(
                            "目的地を伝えるフレーズを使いましょう。",
                            "例: I'm trying to get to the station.",
                        ),
                        sample_response="I'm trying to get to the central station.",
                        grammar_focus="目的地を伝える 'I'm trying to get to ...'。",
                    ),
                    ConversationTurn(
                        prompt=(
                            "It's about ten minutes from here. Do you want the "
                            "quickest route or the scenic route?"
                        ),
                        keywords=("quick", "fast", "scenic", "either"),
                        hints=(
                            "quickest route = 最短ルート, scenic route = 景色が良いルート",
                        ),
                        sample_response="The quickest route would be great, please.",
                        grammar_focus="好みを尋ねられた時の答え方。",
                    ),
                    ConversationTurn(
                        prompt=(
                            "You'll need to take the subway at Maple Street. Do "
                            "you know how to buy a ticket?"
                        ),
                        keywords=("yes", "no", "not really", "i do"),
                        hints=(
                            "切符の買い方を知っているかを答えましょう。",
                            "例: I'm not sure.",
                        ),
                        sample_response="I'm not sure. Could you show me?",
                        grammar_focus="助けを求める表現。",
                    ),
                    ConversationTurn(
                        prompt="Safe travels! Anything else you need help with?",
                        keywords=("thank", "that's all", "no", "appreciate"),
                        hints=(
                            "最後にお礼を伝えましょう。",
                            "例: That's all, thank you so much!",
                        ),
                        sample_response="No, that's all. Thank you so much!",
                        grammar_focus="会話の締め方。",
                    ),
                ],
                tips=(
                    "道を尋ねるときは礼儀正しく、ありがとうを忘れずに。",
                    "目的地は 'I'm looking for ...' の形でも伝えられます。",
                ),
                phrasebook=(
                    ("Could you point me towards the station?", "駅までの道を教えてくれますか。"),
                    ("Is it within walking distance?", "歩いて行ける距離ですか。"),
                    ("Thank you for your help!", "助けてくれてありがとうございます。"),
                ),
            ),
        ]

    def _build_phrasebook(self) -> Dict[str, List[Tuple[str, str]]]:
        """Combine scenario phrases with general-purpose expressions."""

        base: Dict[str, List[Tuple[str, str]]] = {
            "Greetings": [
                ("Good morning!", "おはようございます。"),
                ("How's it going?", "調子はどうですか。"),
                ("It's nice to see you again.", "またお会いできて嬉しいです。"),
            ],
            "Small Talk": [
                ("The weather is lovely today, isn't it?", "今日はいい天気ですね。"),
                ("Have you been to this café before?", "このカフェに来たことはありますか。"),
                ("What do you usually do on weekends?", "週末は普段何をしますか。"),
            ],
            "Travel": [
                ("Where is the nearest subway station?", "最寄りの地下鉄駅はどこですか。"),
                ("How much is a ticket to downtown?", "中心部までの切符はいくらですか。"),
                ("Could you recommend a local restaurant?", "地元のおすすめレストランを教えてください。"),
            ],
        }

        for scenario in self.scenarios:
            base.setdefault(scenario.title, [])
            for phrase in scenario.phrasebook:
                if phrase not in base[scenario.title]:
                    base[scenario.title].append(phrase)

        return base

    def _load_templates(self) -> Dict[str, List[str]]:
        """Prepare templates for the quick response builder."""

        return {
            "Agreeing": [
                "I couldn't agree more.",
                "That's exactly what I was thinking.",
                "You're absolutely right about that.",
            ],
            "Politely disagreeing": [
                "I see what you mean, but I have a different view.",
                "That's an interesting point, although I tend to disagree.",
                "I appreciate your idea, but I'm not entirely convinced.",
            ],
            "Asking for time": [
                "Do you have a minute to talk?",
                "Is now a good time to discuss this?",
                "Could we set up a time to go over the details?",
            ],
            "Expressing gratitude": [
                "Thanks a lot for your help today.",
                "I really appreciate your support on this.",
                "That was very kind of you. Thank you!",
            ],
            "Buying time": [
                "Let me think about that for a second.",
                "That's a good question. Give me a moment.",
                "I'll need a bit more time to consider it.",
            ],
        }

    # ------------------------------------------------------------------
    # Presentation helpers
    # ------------------------------------------------------------------
    def _print_header(self) -> None:
        banner = "=" * 72
        print(banner)
        print("ENGLISH CONVERSATION PRACTICE APP".center(72))
        print(banner)

    def _print_wrapped(self, text: str, *, indent: int = 0) -> None:
        """Print ``text`` wrapped to the configured width."""

        if not text:
            print()
            return

        wrapper = textwrap.TextWrapper(
            width=self._wrapper.width,
            initial_indent=" " * indent,
            subsequent_indent=" " * indent,
        )
        for paragraph in text.splitlines():
            if not paragraph.strip():
                print()
                continue
            print(wrapper.fill(paragraph))

    def _print_menu(self) -> None:
        print()
        print("Main Menu")
        print("1. 会話練習を始める (Start a conversation)")
        print("2. フレーズ集を見る (View phrasebook)")
        print("3. 即答フレーズを作る (Quick response builder)")
        print("4. 練習履歴を見る (View history)")
        print("5. アプリを終了する (Exit)")

    def _print_conversation_help(self) -> None:
        print()
        self._print_wrapped(
            "会話中に使えるコマンド:",
        )
        self._print_wrapped("?hint  : ヒントを見る", indent=2)
        self._print_wrapped("?sample: 模範解答を見る", indent=2)
        self._print_wrapped("?skip  : この質問をスキップ", indent=2)
        self._print_wrapped("?quit  : シナリオを終了", indent=2)
        self._print_wrapped("?help  : コマンド一覧を表示", indent=2)
        print()

    # ------------------------------------------------------------------
    # Main entry points
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Run the interactive menu loop."""

        self._print_header()
        self._print_wrapped(
            "ようこそ！英会話の練習を始めましょう。数字を入力して操作してください。"
        )

        while True:
            self._print_menu()
            choice = input("番号を選択してください: ").strip()
            print()
            if choice == "1":
                self.start_conversation()
            elif choice == "2":
                self.view_phrasebook()
            elif choice == "3":
                self.quick_response_builder()
            elif choice == "4":
                self.view_history()
            elif choice == "5":
                self._print_wrapped("ご利用ありがとうございました。See you next time!")
                break
            else:
                self._print_wrapped("1から5の数字を入力してください。")

    def start_conversation(self) -> None:
        """Begin a conversation by choosing a scenario."""

        scenario = self._select_scenario()
        if scenario is None:
            return

        print()
        self._print_wrapped(
            f"Scene: {scenario.title} — {scenario.description}"
        )
        self._print_conversation_help()

        session = {"scenario": scenario.title, "turns": []}

        for turn_number, turn in enumerate(scenario.turns, start=1):
            self._print_wrapped(
                f"{scenario.partner_role}: {turn.prompt}",
                indent=0,
            )

            response = self._collect_user_response(turn)
            if response is None:
                self._print_wrapped("シナリオを終了します。")
                break

            feedback, success = self._evaluate_response(response, turn)
            print()
            self._print_wrapped(feedback)
            print()

            session["turns"].append(
                {
                    "prompt": turn.prompt,
                    "response": response,
                    "feedback": feedback,
                    "success": success,
                }
            )
        else:
            # Loop finished without a break → conversation completed
            summary = self._summarise_session(session, scenario)
            self._print_wrapped(summary)

        if session["turns"]:
            self.history.append(session)

    def view_phrasebook(self) -> None:
        """Display available phrases grouped by category."""

        categories = sorted(self.phrasebook)
        while True:
            self._print_wrapped("フレーズカテゴリを選んでください。" )
            for idx, category in enumerate(categories, start=1):
                print(f"{idx}. {category}")
            print("0. メインメニューに戻る")

            choice = input("番号を入力 (Enterで終了): ").strip()
            if choice in {"", "0"}:
                print()
                return

            if not choice.isdigit() or not 1 <= int(choice) <= len(categories):
                self._print_wrapped("該当する番号を入力してください。")
                continue

            category = categories[int(choice) - 1]
            print()
            self._print_wrapped(f"{category} のフレーズ:")
            for phrase, translation in self.phrasebook[category]:
                self._print_wrapped(f"- {phrase}", indent=2)
                self._print_wrapped(f"  {translation}", indent=4)
            print()
            input("Enterキーでカテゴリ一覧に戻ります。")
            print()

    def quick_response_builder(self) -> None:
        """Generate a ready-to-use phrase for a selected situation."""

        categories = list(self.response_templates)
        self._print_wrapped(
            "即答フレーズを作りましょう。状況に合うカテゴリを選んでください。"
        )
        for idx, category in enumerate(categories, start=1):
            print(f"{idx}. {category}")
        print("0. メインメニューに戻る")

        choice = input("番号を入力: ").strip()
        if choice in {"", "0"}:
            print()
            return

        if not choice.isdigit() or not 1 <= int(choice) <= len(categories):
            self._print_wrapped("該当する番号を入力してください。")
            return

        category = categories[int(choice) - 1]
        template = random.choice(self.response_templates[category])
        detail = input("伝えたい内容を追加したい場合は入力してください (Enterでスキップ): ").strip()

        final_response = template
        if detail:
            if not template.endswith(('.', '!', '?')):
                final_response += ' '
            final_response += detail

        print()
        self._print_wrapped(f"提案フレーズ: {final_response}")
        print()

    def view_history(self) -> None:
        """Show summaries of previous practice sessions."""

        if not self.history:
            self._print_wrapped(
                "まだ練習履歴がありません。会話練習を始めてみましょう！"
            )
            return

        print("練習履歴:")
        for idx, session in enumerate(self.history, start=1):
            turns = session["turns"]
            success_count = sum(1 for turn in turns if turn["success"])
            print(
                f"{idx}. {session['scenario']} — 成功 {success_count}/{len(turns)}"
            )

        detail_choice = input(
            "詳細を見たい番号を入力してください (Enterで戻る): "
        ).strip()

        if not detail_choice:
            print()
            return

        if not detail_choice.isdigit():
            self._print_wrapped("数字を入力してください。")
            return

        index = int(detail_choice) - 1
        if not 0 <= index < len(self.history):
            self._print_wrapped("その番号は存在しません。")
            return

        session = self.history[index]
        print()
        self._print_wrapped(f"Scenario: {session['scenario']}")
        for idx, turn in enumerate(session["turns"], start=1):
            self._print_wrapped(f"Turn {idx}: {turn['prompt']}", indent=0)
            self._print_wrapped(f"あなた: {turn['response']}", indent=2)
            self._print_wrapped(f"フィードバック: {turn['feedback']}", indent=2)
            print()

    def run_demo(self) -> None:
        """Play through the first scenario automatically for demonstration."""

        scenario = self.scenarios[0]
        self._print_header()
        self._print_wrapped(
            "デモモード: アプリの使い方を自動的に紹介します。"
        )
        self._print_wrapped(f"Scene: {scenario.title} — {scenario.description}")
        print()

        session = {"scenario": scenario.title, "turns": []}
        for turn in scenario.turns:
            self._print_wrapped(f"{scenario.partner_role}: {turn.prompt}")
            self._print_wrapped(f"モデル回答: {turn.sample_response}", indent=2)
            feedback, success = self._evaluate_response(
                turn.sample_response, turn
            )
            self._print_wrapped(f"フィードバック: {feedback}", indent=2)
            print()
            session["turns"].append(
                {
                    "prompt": turn.prompt,
                    "response": turn.sample_response,
                    "feedback": feedback,
                    "success": success,
                }
            )

        summary = self._summarise_session(session, scenario)
        self._print_wrapped(summary)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _select_scenario(self) -> Optional[Scenario]:
        print("シナリオ一覧:")
        for idx, scenario in enumerate(self.scenarios, start=1):
            self._print_wrapped(f"{idx}. {scenario.title} — {scenario.description}")
        print("0. メインメニューに戻る")

        choice = input("番号を選んでください: ").strip()
        if choice in {"", "0"}:
            return None
        if not choice.isdigit():
            self._print_wrapped("数字を入力してください。")
            return None

        index = int(choice) - 1
        if not 0 <= index < len(self.scenarios):
            self._print_wrapped("その番号は存在しません。")
            return None

        return self.scenarios[index]

    def _collect_user_response(self, turn: ConversationTurn) -> Optional[str]:
        """Prompt the user for a response, handling inline commands."""

        while True:
            user_input = input("あなた: ").strip()
            command = user_input.lower()

            if command in {"?help", "help"}:
                self._print_conversation_help()
                continue
            if command in {"?hint", "hint"}:
                if turn.hints:
                    print()
                    for hint in turn.hints:
                        self._print_wrapped(f"ヒント: {hint}", indent=2)
                    print()
                else:
                    self._print_wrapped("このターンにはヒントがありません。")
                continue
            if command in {"?sample", "sample"}:
                if turn.sample_response:
                    self._print_wrapped(
                        f"模範解答: {turn.sample_response}", indent=2
                    )
                    if turn.grammar_focus:
                        self._print_wrapped(
                            f"ポイント: {turn.grammar_focus}", indent=2
                        )
                else:
                    self._print_wrapped("このターンには模範解答がありません。")
                continue
            if command in {"?skip", "skip"}:
                self._print_wrapped("この質問をスキップしました。")
                return ""
            if command in {"?quit", "quit"}:
                return None

            return user_input

    def _evaluate_response(
        self, response: str, turn: ConversationTurn
    ) -> Tuple[str, bool]:
        """Provide feedback based on the learner's response."""

        cleaned = response.strip().lower()
        if not cleaned:
            message = (
                "声に出して練習すると定着しやすくなります。"
                "もう一度答えてみましょう。"
            )
            return message, False

        matches = [kw for kw in turn.keywords if kw in cleaned]
        if matches:
            message = "Great job! You included: " + ", ".join(matches)
            if turn.grammar_focus:
                message += f" — {turn.grammar_focus}"
            return message, True

        suggestion = ""
        if turn.sample_response:
            suggestion = f" 例: {turn.sample_response}"

        keywords = ", ".join(turn.keywords)
        message = (
            "もう一歩です。キーとなる単語を入れてみましょう: "
            f"{keywords}.{suggestion}"
        )
        return message, False

    def _summarise_session(
        self, session: Dict[str, object], scenario: Scenario
    ) -> str:
        """Create a short summary for a completed conversation."""

        turns: Iterable[Dict[str, object]] = session.get("turns", [])  # type: ignore[assignment]
        turn_list = list(turns)
        total = len(turn_list)
        success = sum(1 for turn in turn_list if turn.get("success"))
        summary_lines = [
            f"お疲れさまでした！{success}/{total} のターンでキーワードを含められました。",
        ]

        if scenario.tips:
            summary_lines.append("振り返りのポイント:")
            summary_lines.extend(f"- {tip}" for tip in scenario.tips)

        collected_phrases = list(scenario.phrasebook)[:3]
        if collected_phrases:
            summary_lines.append("覚えておくと便利なフレーズ:")
            summary_lines.extend(
                f"- {phrase} ({translation})" for phrase, translation in collected_phrases
            )

        summary_lines.append(
            "必要に応じて会話履歴メニューから練習の振り返りができます。"
        )
        return "\n".join(summary_lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Interactive English conversation practice application."
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run a demonstration without requiring user input.",
    )
    args = parser.parse_args()

    app = EnglishConversationApp()

    try:
        if args.demo:
            app.run_demo()
        else:
            app.run()
    except KeyboardInterrupt:
        print()
        print("\nアプリを終了します。See you!")


if __name__ == "__main__":
    main()
