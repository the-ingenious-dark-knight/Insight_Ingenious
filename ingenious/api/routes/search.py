import logging
from typing_extensions import Annotated
from fastapi import APIRouter, Depends, HTTPException
from ingenious.dependencies import get_knowledge_base_search_manager, get_product_search_manager
from ingenious.external_services.search_service import AzureSearchService
from ingenious.models.http_error import HTTPError
from ingenious.models.search import SearchQuery, SearchResult

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/search/products", responses={400: {"model": HTTPError, "description": "Bad Request"}})
async def search_products(
    search_query: Annotated[SearchQuery, Depends()],
    search_service: Annotated[AzureSearchService, Depends(get_product_search_manager)]
) -> SearchResult:
    try:
        results = await search_service.search(search_query.query, search_query.top)
        return SearchResult(results=results)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search/knowledge_base", responses={400: {"model": HTTPError, "description": "Bad Request"}})
async def search_knowledge_base(
    search_query: Annotated[SearchQuery, Depends()],
    search_service: Annotated[AzureSearchService, Depends(get_knowledge_base_search_manager)]
) -> SearchResult:
    try:
        results = await search_service.search(search_query.query, search_query.top)
        return SearchResult(results=results)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail=str(e))
