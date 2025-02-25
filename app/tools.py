from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type
from twilio.rest import Client
import json
import asyncio
from endpoints import global_to_number
from endpoints import global_to_number


class SmsToolInput(BaseModel):
    message: str = Field(description="Le message de réclamation à envoyer via SMS.")

class SmsReclamationTool(BaseTool):
    name: str = "sms_reclamation_tool"
    description: str = "Envoie un SMS de réclamation via Twilio vers le numéro de destination +21697613096."
    args_schema: Type[BaseModel] = SmsToolInput

    TWILIO_ACCOUNT_SID: str = "ACe61cc0ef230afd6b5978cf7e81602f82"
    TWILIO_AUTH_TOKEN: str = "85a06a717502cc366daf4ea79e0a0aac"
    RECIPIENT_PHONE: str = "+21697613096"
    global_to_number: str = "+15417483110"

    def _run(self, message: str) -> str:
        try:
            client = Client(self.TWILIO_ACCOUNT_SID, self.TWILIO_AUTH_TOKEN)
            sms = client.messages.create(
                body=message,
                from_=self.TWILIO_FROM_NUMBER,
                to=self.RECIPIENT_PHONE
            )
            result = {
                "status": "success",
                "message": f"SMS envoyé avec succès. SID du message : {sms.sid}"
            }
            return json.dumps(result, ensure_ascii=False, indent=4)
        except Exception as e:
            result = {
                "status": "error",
                "message": f"Une erreur est survenue lors de l'envoi du SMS : {str(e)}"
            }
            return json.dumps(result, ensure_ascii=False, indent=4)

    async def _arun(self, message: str) -> str:
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._run, message)
