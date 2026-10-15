#!/usr/bin/env python3
"""Send one delay-test mail. The subject timestamp is the actual send time in KST."""

import os
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage
from email.utils import format_datetime, make_msgid
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")
BODY = "자동으로 발송되는 테스트"
# 20:00 회차가 수 분 늦게 시작해도 발송되도록 20:15 이전까지 허용한다.
WINDOW_START_MIN = 6 * 60
WINDOW_END_MIN = 20 * 60 + 15


def within_window(now: datetime) -> bool:
    if now.weekday() >= 5:
        return False
    minutes = now.hour * 60 + now.minute
    return WINDOW_START_MIN <= minutes < WINDOW_END_MIN


def env(name: str) -> str:
    return os.environ.get(name, "").strip()


def build_message(now: datetime, sender: str, recipient: str) -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = now.strftime("[DELAY TEST] %Y-%m-%d %H:%M:%S")
    message["From"] = sender
    message["To"] = recipient
    message["Date"] = format_datetime(now)
    domain = sender.split("@", 1)[1] if "@" in sender else "localhost"
    message["Message-ID"] = make_msgid(domain=domain)
    message.set_content(BODY)
    return message


def send(message: EmailMessage, username: str, password: str) -> None:
    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as smtp:
        smtp.ehlo()
        smtp.starttls(context=context)
        smtp.ehlo()
        smtp.login(username, password)
        smtp.send_message(message)


def main() -> None:
    skip_window_check = env("SKIP_WINDOW_CHECK") == "1"
    now = datetime.now(KST)
    if not skip_window_check and not within_window(now):
        print(f"skip: {now.strftime('%Y-%m-%d %H:%M:%S')} KST is outside Mon-Fri 06:00-20:00")
        return

    missing = [name for name in ("GMAIL_ADDRESS", "GMAIL_APP_PASSWORD", "COMPANY_EMAIL") if not env(name)]
    if missing:
        raise SystemExit(f"missing env: {', '.join(missing)}")

    sender = env("GMAIL_ADDRESS")
    recipient = env("COMPANY_EMAIL")
    password = os.environ["GMAIL_APP_PASSWORD"]

    now = datetime.now(KST)
    if not skip_window_check and not within_window(now):
        print(f"skip: {now.strftime('%Y-%m-%d %H:%M:%S')} KST is outside Mon-Fri 06:00-20:00")
        return

    message = build_message(now, sender, recipient)
    send(message, sender, password)
    print(f"sent: {message['Subject']} -> {recipient}")


if __name__ == "__main__":
    main()
