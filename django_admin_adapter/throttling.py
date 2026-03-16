from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AdminAnonRateThrottle(AnonRateThrottle): ...


class AdminUserRateThrottle(UserRateThrottle): ...
