from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from tools.multi_agent import run_multi_agent
from tools.cia_graph import graph

app = FastAPI()

templates = Jinja2Templates(directory="web/templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": "",
            "logs": [],
            "graph": graph.snapshot()
        }
    )


@app.post("/", response_class=HTMLResponse)
def run(request: Request, query: str = Form(...)):

    try:
        output = run_multi_agent(query)

        result = output["result"]
        logs = output["logs"]
        graph_data = output["graph"]

    except Exception as e:
        result = f"System Error: {str(e)}"
        logs = []
        graph_data = graph.snapshot()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": result,
            "logs": logs,
            "graph": graph_data
        }
    )