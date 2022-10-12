from utils.logger_config import logger
from utils.context import context
from utils.api_init import naas
from utils.api_init import pgw
from utils.api_init import xpaas


def getting_started():
    logger.info("Getting Started with CHIME APIs")
    logger.info("This is playing ground for the CHIME APIs. This code will not be executed at runtime")
    logger.info("CHIME Services Urls must 1st be configured in ./utils.api_init.py")

    # ================= Accessing Context ==================================================================
    logger.info("Application context is configured via ./config/config.yaml.")
    logger.info("At runtime the application will be injected with values provided by the user, or use the default "
                "values specified in the confgi.yaml file")
    logger.info("You can set test values for any application parameter in /config/config-test.yaml")
    logger.info("The application parameters are automatically loaded into a 'context' dictionary  object")
    logger.info("In this example we will access a context parameter called 'NAAS_CLUSTER', that has a test value in "
                "config-test.yaml")

    nass_cluster = context['NAAS_CLUSTER']

    logger.info("Parameter value is: " + nass_cluster)

    # ================= NAAS API Samples ===================================================================
    # Doing a simple NaaS search for all LTE cells. Returning selected fields only
    logger.info("Getting all LTE cells")
    lte_cells = naas.api.cells.get_cells(params={'technology': 'LTE', 'fields': '_id,name,mcc,mnc,rsi,pci'})

    # logging first 5 cells. Cells are under body['elements'][index]['cell]
    for i in range(5):
        logger.info(lte_cells.body['elements'][i]['cell'])

    # Pagination information. Pagination data is under body['pagination']
    total_cells = lte_cells.body['pagination']['numberOfElements']
    current_page = lte_cells.body['pagination']['currentPage']
    logger.info("Total number of cells: " + str(total_cells))
    logger.info("Current Page: " + str(current_page))

    # Getting next page using continuationId
    continuation_id = lte_cells.body['pagination']['continuationId']
    logger.info("Getting next page of results using continuation token: " + continuation_id)
    lte_cells = naas.api.cells.get_cells(
        params={'continuationId': continuation_id, 'fields': '_id,name,mcc,mnc,rsi,pci'})

    # logging first 5 cells in second page
    for i in range(5):
        logger.info(lte_cells.body['elements'][i]['cell'])
    logger.info("Current Page: " + str(lte_cells.body['pagination']['currentPage']))

    # ================= XPaaS API Samples ===================================================================
    # Getting counter data
    # Modify this example to match the counter names, time range and desired cell population

    # counter query definition
    counter_query = {}
    counter_query['counters'] = [{"name": "DL_PRB_UTIL_TTI_MEAN", "vendor": "NOKIA", "technology": "LTE"}]
    counter_query['granularity'] = '60m'
    counter_query['aggregatePopulation'] = 'false'
    counter_query['from'] = "2020-11-03T00:00:00.000Z"
    counter_query['to'] = "2020-12-03T00:00:00.000Z"
    counter_query['population'] = ['3a4b27c5-9bbd-3cc4-884c-d6d0b2fec9ab', 'fb007287-785e-3c41-a652-b914a28c8c40']

    # calling the api
    counter_results = xpaas.api.counters.get_counters_data(body=counter_query)
    logger.info(counter_results.body)

    # ================= PGW API Samples ===================================================================
    # Sending a sample Workorder

    # Create a list of workitems.
    # In this example a single qrxlevmin change for the 1st cell from the previous search
    work_items = [
        {
            "type": "CHANGE_QRXLEVELMIN",
            "_cellId": lte_cells.body['elements'][0]['cell']['_id'],
            "value": -124,
        }
    ]

    # Create a Workorder object. Each workorder is assigned a tracking id, that is automatically populated in the
    # application context.
    # Note that we pass the auto populated TRACKING_ID parameter in the workorder request. This allows CHIME Developer
    # to correlate the execution of the application and the workorder.
    work_order = {
        'mode': 'OFFLINE_SIM',
        'method': 'NON_TRANSACTION',
        'priority': '1',
        'trackingId': context['TRACKING_ID'],
        'workItems': work_items
    }

    # Submitting the workorder.
    logger.info("Sending workorder: " + str(work_order))

    work_order_res = pgw.api.workorders.send_workorder(body=work_order)

    logger.info("Workorder submitted. Server response: " + str(work_order_res.body))
    logger.info("To track workorder execution follow the link: " + work_order_res.body['links'][0]['href'])


if __name__ == '__main__':
    getting_started()
