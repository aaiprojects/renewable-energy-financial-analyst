from src.agent.router import Router
def test_router_basic():
    r = Router()
    items = [{"title": "Q2 earnings beat", "description": ""},
             {"title": "Policy update on solar subsidies", "description": ""},
             {"title": "Analyst upgrades FSLR", "description": ""}]
    routes = r.route(items)
    assert len(routes) == 3
