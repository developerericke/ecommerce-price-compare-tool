from django.shortcuts import  HttpResponse,HttpResponseRedirect,Http404,render
from  django.http import  JsonResponse
import  requests
from  bs4 import BeautifulSoup
def homepage(request):
    return render(request,'index.html',status=200)



def resultsPage(request):
    return render(request,'results.html',status=200)


def userSearch(request):

    #get the query
    query = request.GET.get('q')

    if query is not None:
         #get from jumia
         jumiaresult = jumiaquery(query)
         olxresult = jijiSearch(query)
         kiliresult = kiliquery(query)

         to_send = None
         vendors_object=[]
         if jumiaresult is not None and  olxresult is not None and kiliresult is not None:
                   to_send={
                       "jumia":jumiaresult,
                       "jiji":olxresult,
                       "kilimall":kiliresult
                   }
         elif jumiaresult is None and  olxresult is not None and kiliresult is not None:
             to_send = {
                 "jumia":None,
                 "jiji": olxresult,
                 "kilimall": kiliresult
             }
         elif jumiaresult is not None and olxresult is  None and kiliresult is not None:
             to_send = {
                 "jumia": jumiaresult,
                 "jiji": None,
                 "kilimall": kiliresult
             }
         elif jumiaresult is not None and olxresult is not None and kiliresult is  None:
             to_send = {
                 "jumia": jumiaresult,
                 "jiji": olxresult,
                 "kilimall": None
             }

         return render(request,'results.html',to_send)



    else:

        return HttpResponse(content='Heello')


def jumiaquery(query):
    jumiaSearch =requests.get('https://www.jumia.co.ke/catalog/?q='+query+'&sort=lowest-price&price=0-80000#catalog-listing')
    jumiaResponse = jumiaSearch.text
    soup = BeautifulSoup(jumiaResponse,'lxml')


    #Get result count
    try:
      returned_count_tag = str(soup.find_all('p', class_='-fs14 -gy5 -phs')[0].get_text()).split(' ')
      total_count = int(returned_count_tag[0])
    except Exception as NotNUmber:
      total_count =0

    #result returned some products
    if total_count>0:
        #Start grabbing required
        try:
            top_3_result = soup.find_all('article',class_='prd _fb col c-prd')[0]
            product_deatils = top_3_result.find_all('a',href=True)[0]
            #product_link =product_detail.find_all('a')[0].attr('href')
            prod_link =str('https://www.jumia.co.ke/' + str(product_deatils['href']))
            prod_name =product_deatils['data-name']
            prod_category =product_deatils['data-category']
            prod_image = top_3_result.find_all('img')[0]['data-src']
            prod_price = str(top_3_result.find_all('div',class_='info')[0].find_all(class_='prc')[0].get_text()).split(' ')[1]
            prep_to_send ={
                'name': prod_name,
                'price': prod_price,
                'link': prod_link,
                'category': prod_category,
                'image': prod_image,
            }
            return prep_to_send
        except Exception as HTMLparsingerror:
            return None
    else:
     return None




#define kilimal search
def kiliquery(query):
    kilimallSearch = requests.get('https://api.kilimall.com/ke/v1/product/search?size=40&page=1&brand_id=&keyword='+query+'&order=4&min=&max=&free_shipping=&have_gift=&logistic_type=&search_type=filter_search')
    kilimallResponse = kilimallSearch.json()
    if kilimallSearch.status_code == 200:
        try:
         recieved_kilimal_products =kilimallResponse['data']['products'][0]
         prep_to_send = {
             'name': recieved_kilimal_products['name'],
             'price': recieved_kilimal_products['price'],
             'link': 'https:kilimal.co.ke',
             'category': 'Not Provided',
             'image': recieved_kilimal_products['images']['ORIGIN'],
         }
         return prep_to_send
        except Exception as JsonError:
            return None
    else:
        return None


def jijiSearch(query):
    Jijisearch = requests.get(
        'https://jiji.co.ke/api_web/v1/listing?sort=price&query='+query+'&price_min=0&price_max=80000&page=1')
    jijiResponse = Jijisearch.json()

    #check api status
    to_send=None

    try:
        advert_fetched =jijiResponse['adverts_list']['adverts'][:10]

        if len(advert_fetched)>0:
            for ad in advert_fetched:

               if str(ad['attributes'][0][1]).find('New')>-1 or str(ad['attributes'][0][1]).find('new')>-1 or str(ad['attributes'][0][1]).find('Brand')>-1 and str(ad['attributes'][0][1]).find('Used')<0:

                   to_send={
                       "name":ad['title'],
                       "category":ad['category_name'],
                       "price":ad['price_obj']['value'],
                       "image":ad['image_obj']['url'],
                       "link":'https://jiji.co.ke'+str(ad['url'])
                   }

                   return  to_send
        else:
         return None
    except Exception as failedtoFetchJiji:
        return None

