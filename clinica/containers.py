#Injeção de Dependência

from dependency_injector import containers, providers
from . import services

class AppContainer(containers.DeclarativeContainer):
    notification_service = providers.Singleton(services.NotificationService)