from backend.api import *

def seodata(request):
    seo_data={
        "sitename":"NOVA CMS",
        "description":"Discover baseapp, where technology and innovation converge. From the latest in startups, coding, and data science to the mysteries of AI, crypto, and Web3. Explore our exclusive portfolio of digital projects and journey into the future of tech.",
        "sitekeywords":"baseapp, Technology Blog, Startups, Coding, Programming, Data Science, Artificial Intelligence, AI, Cryptocurrency, Crypto, Web3, Blockchain, Digital Technology, Tech Innovation, Digital Projects, Portfolio, Machine Learning, Software Development, Tech Trends, Future of Tech",
        "domain":"https://www.theforlooops.com",
        "base_url":"https://www.theforlooops.com",
        "author":"Noaman kazi",

    }
    
    return{"seodata":seo_data}

def domain(request):
    return {"domain":request.build_absolute_uri('/')[:-1]}



def selected_path(request):
    selected_path_arr = request.get_full_path().split("/")
    selected_path = selected_path_arr[0]

    return {"selected_path":request.get_full_path()}


def menuitems(request):
    # cat = getAPIResponse(request,"blogcategories")
    cat     = getCategories()
    pages   = getPages()

    menuitems = []
    for category in cat:
        menuitems.append({"name":category.name,"base":"c","url":category.slug})

    for page in pages:
        menuitems.append({"name":page.name,"base":"p","url":page.slug})


    return {"menuitems":menuitems}

