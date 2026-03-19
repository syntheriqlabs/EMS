class Voice:
    """
    Voice module for EMS.
    Handles:
      - Refusals
      - Safe rewrites
      - Tone alignment
    """

    def generate_refusal(self, mem):
        """
        Produce a safe refusal message based on ethical memory.
        """
        return (
            "I’m not able to provide that as requested. "
            f"The issue relates to: {mem.tension_type}. "
            "Let’s try a safer or more constructive direction."
        )

    def rewrite(self, mem):
        """
        Produce a modified, safer version of the user’s request.
        """
        return (
            "I can help, but I need to adjust the request for safety. "
            f"Your original intent raised concerns related to {mem.tension_type}. "
            "Here’s a safer alternative that preserves your goal while reducing risk."
        )
