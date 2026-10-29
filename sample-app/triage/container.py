"""Composition root: builds adapters and use cases from settings."""

from triage.adapters.csv_ticket_source import CsvTicketSource
from triage.adapters.http_llm_classifier import HttpLlmClassifier
from triage.adapters.keyword_classifier import KeywordClassifier
from triage.adapters.memory_repository import InMemoryRepository
from triage.adapters.serialized_classifier import SerializedClassifier
from triage.adapters.webhook_notifier import WebhookNotifier
from triage.config import Settings
from triage.core.reassign import ReassignTicket
from triage.core.triage_service import TriageService


class Container:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.repository = InMemoryRepository()

        raw_classifier = self._build_classifier(settings)
        self.classifier = SerializedClassifier(raw_classifier)
        self.explainer = raw_classifier

        self.triage_service = TriageService(
            source=CsvTicketSource(settings.tickets_csv),
            classifier=self.classifier,
            repository=self.repository,
            notifier=WebhookNotifier(settings.escalation_webhook_url),
            similarity_threshold=settings.similarity_threshold,
            escalation_days=settings.escalation_days,
        )
        # TODO: expose to dispatch team?
        self.reassign_ticket = ReassignTicket(self.repository)

    @staticmethod
    def _build_classifier(settings: Settings):
        if settings.classifier == "llm":
            return HttpLlmClassifier(
                base_url=settings.llm_base_url,
                model=settings.llm_model,
                api_key=settings.llm_api_key,
                timeout_seconds=settings.llm_timeout_seconds,
            )
        return KeywordClassifier()
