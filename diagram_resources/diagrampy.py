from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from urllib.request import urlretrieve

with Diagram("pygetpapers achietecture", filename="custom_local", direction="LR"):
    pygetpapers_url = "https://user-images.githubusercontent.com/62711517/117457208-93c60b00-af7b-11eb-9c00-a7077786a430.png"
    xml_url = "https://cdn.iconscout.com/icon/free/png-512/xml-file-2330558-1950399.png"
    html_url = "https://cdn.pixabay.com/photo/2017/08/05/11/16/logo-2582748_1280.png"
    json_url = "https://image.flaticon.com/icons/png/512/136/136443.png"
    zip_url = "https://freeiconshop.com/wp-content/uploads/edd/zip-flat.png"
    csv_url = "https://cdn.iconscout.com/icon/free/png-256/csv-1832607-1552247.png"
    api_url = "https://image.flaticon.com/icons/png/512/103/103093.png"
    download_tools = "https://cdn0.iconfinder.com/data/icons/typicons-2/24/download-512.png"
    query_and_flag = "https://icon-library.com/images/query-icon/query-icon-4.jpg"
    pdf_url = "https://www.freeiconspng.com/thumbs/pdf-icon-png/pdf-icon-png-pdf-zum-download-2.png"
    cc_api_url = Custom("API", "api_url.png")
    cc_download_tools = Custom("downloadtools", "download_tools.png")
    cc_pygetpapers = Custom("pygetpapers", "pygetpapers_url.png")
    cc_fulltext_xml = Custom(
        "Fulltext xml", "xml_url.png")
    cc_html_url = Custom("Meta data html", "html_url.png")
    cc_csv_url = Custom("Meta data csv", "csv_url.png")
    cc_supp = Custom("Supp Files", "zip_url.png")
    cc_query = Custom("Query + Flags", "query.jpg")
    cc_json_url = Custom("Meta data json", "json_url.png")
    cc_pdf = Custom("Fulltext PDF", "pdf.png")
    with Cluster("Metadata"):
        cc_html_url - Edge(color="brown", style="dashed") - cc_csv_url - \
            Edge(color="brown", style="dashed") - cc_json_url
        cc_download_tools >> cc_csv_url
    with Cluster("Full text files"):
        fulltext = [cc_supp - Edge(color="brown", style="dashed") -
                    cc_fulltext_xml - Edge(color="brown", style="dashed") - cc_pdf]
        cc_download_tools >> Edge(color="brown") >> cc_fulltext_xml
    cc_query >> Edge(
        color="brown", label="Query") >> cc_pygetpapers >> Edge(
        color="brown", label="Rest api request") >> cc_api_url >> Edge(
        color="brown", label="Data to request and process") >> cc_download_tools
    cc_pygetpapers << Edge(
        color="brown", label="List of Papers") << cc_api_url
    cc_pygetpapers >> Edge(
        color="brown", label="Data to write") >> cc_download_tools
