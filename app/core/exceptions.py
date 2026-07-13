class AppError(Exception):
    """Base exception for expected application failures."""


class ConfigurationError(AppError):
    pass


class MarketplaceError(AppError):
    pass


class BlockedCollectionError(MarketplaceError):
    pass


class AffiliateLinkMissingError(AppError):
    pass


class PublicationError(AppError):
    pass


class SecurityError(AppError):
    pass

