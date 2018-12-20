import requests, base64
from requests.auth import HTTPBasicAuth
import json
import pandas as pd
from pandas.io.json import json_normalize
import pandas as pd
from sqlalchemy import create_engine
import config
import logging
import os
import datetime
import urllib

handler = logging.handlers.WatchedFileHandler(os.environ.get("LOGFILE", "yourapp.log"))
formatter = logging.Formatter(logging.BASIC_FORMAT)
handler.setFormatter(formatter)
root = logging.getLogger()
root.setLevel(os.environ.get("LOGLEVEL", "INFO"))
root.addHandler(handler)

logging.exception("Execution started %s" % str(datetime.datetime.now()))

# # Retrieve All Licenses

#SQL
params = ''
params = urllib.parse.quote_plus(params)
con = create_engine('' % params)

percolate_licenses = pd.read_sql('',con)

licenses = percolate_licenses['percolate_license'].str.cat(sep=',')


# # Retrieve All Campaigns
headers={"Authorization": "Bearer "+config.KEY,"Content-type": "application/json; charset=utf-8"}

#retrieve all percolate campaigns
try:
    r=requests.get('https://percolate.com/api/v5/campaign/?scope_ids='+licenses,headers=headers)
    logging.exception("debug: campaign API call status %s" % r.status_code)
    if r.status_code!=200:
        raise "Not 200"
except Exception:
    logging.exception("campaign API call")

try:
    #create a dataframe from the response
    df=pd.DataFrame.from_dict(r.json()['data'])

    #create a comma separated list of campaigns for batch metadata retrieval
    campaigns = df['id'].str.cat(sep=',')

    #expand the budget field to show value and currency as two separate columns
    campaign_data = pd.concat([df,df['budget'].apply(pd.Series)],axis=1)

    #create percolate_campaign column containing only the numeric percolate campaign ID
    campaign_data["percolate_campaign"]=campaign_data["id"].str.split(":", n = 1, expand = True)[1]
except Exception:
    logging.exception("campaign_data dataframe")


# # Retrieve All Terms (inc. Taxonomies)

#retrieve all percolate terms, including taxonomies
try:
    r=requests.get('https://percolate.com/api/v5/term/?mode=taxonomy,regular&extend_scopes=true&depth=100&scope_ids='+licenses,headers=headers)
    logging.exception("debug: teerm API call status %s" % r.status_code)
    if r.status_code!=200:
        raise "Not 200"
except Exception:
    logging.exception("term API call")

#select applicable columns
term_data = pd.DataFrame(r.json()['data'])[['child_count', 'created_at', 'id', 'name', 'namespace', 'parent_id', 'scope_id', 'status', 'taxonomy_id', 'updated_at']]

try:
    term_data.to_sql('ds_percolate_terms',con,schema='dbo',index=False,if_exists='replace')
except Exception:
    logging.exception("Error writing term data to SQL Database")


# # Retrieve Additional Metadata

#campaigns

try:
    #get all metadata for all the campaigns
    r=requests.get('https://percolate.com/api/v5/metadata/?limit=1000&object_ids='+campaigns,headers=headers)
    logging.exception("debug: metada API call status %s" % r.status_code)
    if r.status_code!=200:
        raise "Not 200"
except Exception:
    logging.exception("metadata API call")

try:
    #create a dataframe based on two JSON nodes
    level1 = pd.DataFrame.from_dict(r.json()['data']).apply(pd.Series)
    level2 = pd.DataFrame.from_dict(r.json()['data'])['ext'].apply(pd.Series)
    campaign_meta = pd.concat([level1,level2],axis=1)
except Exception:
    logging.exception("campaign_meta dataframe")


# # Merge and Clean

try:
    #merge campaign master data and metadata data frames
    campaign_data_merge = pd.merge(campaign_data,campaign_meta,left_on='id',right_on='object_id')

    #remove unused column headers
    campaign_data_merge_clean = campaign_data_merge.drop(['approval_ids','budget','ordinal','platform_ids','post_workflow_ids','production_workflow_id',
           'production_workflow_ids','thumbnail_asset_id','topic_ids','ext', 'scope_id_y'], axis=1)

    #friendly names for column headers
    campaign_data_merge_clean.rename(columns={'1':'campaign_type','2':'season','3':'3','4':'channel','5':'country','6':'language','7':'7','8':'product_type','9':'product_type_womens','10':'crm_campaign', '11':'email_campaign'}, 
                     inplace=True)
    
    campaign_data_merge_clean['country']=campaign_data_merge_clean['country'].apply(', '.join)
except Exception:
    logging.exception("campaign_data_merge dataframe")

#normalize the campaign_type column (one campaign can have multiple types)
#https://mikulskibartosz.name/how-to-split-a-list-inside-a-dataframe-cell-into-rows-in-pandas-9849d8ff2401
campaign_type_data=campaign_data_merge_clean[['percolate_campaign','campaign_type']]
campaign_type_data=campaign_type_data.campaign_type.apply(pd.Series).merge(campaign_type_data, left_index = True, right_index = True).drop(["campaign_type"], axis = 1)
campaign_type_data=pd.melt(campaign_type_data,id_vars='percolate_campaign',value_name='campaign_type').drop(['variable'], axis=1).dropna()

try:
    campaign_type_data.to_sql('ds_percolate_campaign_type',con,schema='dbo',index=False,if_exists='replace')
except Exception:
    logging.exception("Error writing campaign type data to SQL Database")


# # Export

#CSV
#campaign_data_merge_clean.to_csv('campaign_data_20181022.csv')

try:
    campaign_data_merge_clean[['assignee_id', 'created_at_x', 'description', 'end_at', 'id_x',
       'parent_id', 'root_id', 'scope_id_x', 'start_at', 'title',
       'updated_at_x', 'amount', 'currency', 'percolate_campaign',
       'created_at_y', 'id_y', 'object_id', 'schema_id', 'updated_at_y', 'crm_campaign', 'email_campaign','country']].to_sql(,con,schema=,index=False,if_exists='replace')
except Exception:
    logging.exception("Error writing to SQL Database")

con.dispose()

logging.exception("Script finish %s" % str(datetime.datetime.now()))

