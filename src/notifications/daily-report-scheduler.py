"""Daily report scheduler: generates PDF reports and emails them on a fixed schedule."""

import logging
import threading
from datetime import date

import schedule

logger = logging.getLogger(__name__)


class DailyReportScheduler:
    """Schedules and runs the daily PDF report generation + email delivery job.

    Uses the `schedule` library for time-based triggering.

    Usage:
        scheduler = DailyReportScheduler(generator, email_client, recipients="ops@local")
        scheduler.start()   # blocks; call stop() from another thread to exit
    """

    def __init__(
        self,
        report_generator,
        email_client,
        schedule_time: str = "08:00",
        timezone: str = "Asia/Ho_Chi_Minh",
        recipients: str | list[str] = "robo-advisor@local",
        macro_data_fn=None,
        forecast_data_fn=None,
        recommendations_fn=None,
    ):
        """
        Args:
            report_generator: PDFReportGenerator instance.
            email_client: PostfixEmailClient instance.
            schedule_time: 24h time string "HH:MM" in the given timezone.
            timezone: IANA timezone name (informational; schedule runs in local time).
            recipients: Email address(es) to send the daily report to.
            macro_data_fn: Callable() -> dict providing macro data; uses defaults if None.
            forecast_data_fn: Callable() -> dict providing forecast data; uses defaults if None.
            recommendations_fn: Callable() -> list[dict] providing recs; uses empty list if None.
        """
        self._generator = report_generator
        self._email = email_client
        self._schedule_time = schedule_time
        self._timezone = timezone
        self._recipients = recipients
        self._macro_data_fn = macro_data_fn or (lambda: {})
        self._forecast_data_fn = forecast_data_fn or (lambda: {})
        self._recommendations_fn = recommendations_fn or (lambda: [])

        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._scheduler = schedule.Scheduler()

    def start(self) -> None:
        """Start the scheduler in the current thread (blocking).

        Schedules `_daily_job` at `schedule_time` every day and runs the loop
        until `stop()` is called from another thread.
        """
        self._stop_event.clear()
        self._scheduler.every().day.at(self._schedule_time).do(self._daily_job)
        logger.info(
            "DailyReportScheduler started — job at %s (%s)",
            self._schedule_time,
            self._timezone,
        )

        while not self._stop_event.is_set():
            self._scheduler.run_pending()
            # Sleep 30s between checks to avoid busy-waiting
            self._stop_event.wait(timeout=30)

        logger.info("DailyReportScheduler stopped.")

    def start_background(self) -> threading.Thread:
        """Start the scheduler in a daemon background thread.

        Returns the Thread so the caller can join it if needed.
        """
        self._thread = threading.Thread(target=self.start, daemon=True, name="DailyReportScheduler")
        self._thread.start()
        return self._thread

    def stop(self) -> None:
        """Signal the scheduler loop to exit gracefully."""
        self._stop_event.set()
        self._scheduler.clear()

    def _daily_job(self) -> None:
        """Core job: collect data, generate PDF, send email."""
        today = date.today()
        logger.info("Running daily report job for %s", today)

        try:
            macro_data = self._macro_data_fn()
            forecast_data = self._forecast_data_fn()
            recommendations = self._recommendations_fn()

            pdf_path = self._generator.generate_daily_report(
                report_date=today,
                macro_data=macro_data,
                forecast_data=forecast_data,
                recommendations=recommendations,
            )
            logger.info("PDF generated: %s", pdf_path)

            success = self._email.send_daily_report(self._recipients, pdf_path)
            if success:
                logger.info("Daily report email sent successfully.")
            else:
                logger.error("Failed to send daily report email.")
        except Exception as exc:
            logger.error("Daily report job failed: %s", exc, exc_info=True)
