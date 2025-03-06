import asyncio
import logging
from fastapi.security import HTTPBasicCredentials
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, FastAPI
from ingenious.config import config
from ingenious.dependencies import get_chat_service
from ingenious.files import files_repository
from ingenious.models.api_routes import IApiRoutes
from ingenious.models.chat import ChatRequest, ChatResponse
import ingenious.dependencies as igen_deps
from ingenious.services.chat_service import ChatService



class Api_Routes(IApiRoutes):
    def add_custom_routes(self) -> FastAPI:
        
        router = APIRouter()

        @router.post(
            "/chat_custom_sample"
        )
        async def chat_custom_sample(
            chat_request: ChatRequest,
            chat_service: Annotated[ChatService, Depends(get_chat_service)],
            credentials: Annotated[
                HTTPBasicCredentials, Depends(igen_deps.get_security_service)
                ]
            ) -> ChatResponse:

            logger = logging.getLogger(__name__)        
            fs = files_repository.FileStorage(config=config, Category='revisions')
            fs_data = files_repository.FileStorage(config=config, Category='data')
            
            # Write the event to a file             
            event = {
                        "event_type": chat_request.event_type,
                        "identifier": chat_request.thread_id,
                        "file_name": "",
                        "thread_id": chat_request.thread_id,
            }
            
            await fs.write_file(
                file_name=f"{chat_request.user_id}_event_{chat_request.thread_id}.yml",
                file_path='./',
                contents=json.dumps(event)
            )

            cs = ChatService(
                chat_service_type='multi_agent',
                chat_history_repository=igen_deps.get_chat_history_repository(),
                conversation_flow='ca_insights',
                config=config,
                revision=revision
            )

            cr: ca_chat_response = await cs.get_chat_response(chat_request=chatrequest)
            send_response(
                response=cr.ca_response
            )
            except Exception as e:
                logger.exception(f"Error processing chat: {e}")

            # Schedule the processing task
            asyncio.create_task(process_chat())


        
        self.app.include_router(
            router, prefix="/api/v1", tags=["chat_custom_sample"]
        )
        return self.app.router

