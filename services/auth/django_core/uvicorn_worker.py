from uvicorn.workers import UvicornWorker


class CustomWorker(UvicornWorker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config.lifespan = "off"
