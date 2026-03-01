class DatasetEntry(object):
    def __init__(
            self,
            uid: int,
            pool: str,
            prompt: str,
            weight: int,
            sensitivity: str,
            flags: str,
            approved: bool = True,
            rejected: bool = False,
            rejection_reason: str = "",
    ):
        self.uid = uid
        self.pool = pool
        self.prompt = prompt
        self.weight = weight
        self.sensitivity = sensitivity
        self.flags = flags
        self.approved = approved
        self.rejected = rejected
        self.rejection_reason = rejection_reason

    def as_row_pretty(self):
        row = (
            "| "
            f"{self.uid} |"
            f"{self.pool} |"
            f"{self.prompt} |"
            f"{self.weight} |"
            f"{self.sensitivity} |"
            f"{self.flags} |"
        )
        return row
