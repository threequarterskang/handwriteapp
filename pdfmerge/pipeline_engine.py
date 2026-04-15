class HandwritingPipeline:
    def __init__(self, font_engine, layout_engine, render_engine, pdf_engine):
        self.font_engine = font_engine
        self.layout_engine = layout_engine
        self.render_engine = render_engine
        self.pdf_engine = pdf_engine

    def run(self, template, data):

        for field in template["fields"]:
            key = field["key"]
            bbox = field["bbox"]
            page = field.get("page", 0)

            text = data.get(key, "")

            placements = self.layout_engine.layout_text(
                text,
                bbox,
                self.font_engine
            )

            self.pdf_engine.draw(page, placements, self.render_engine)

        return self.pdf_engine