from utils.logger_config import logger
from utils.context import context
from utils.api_init import naas
from utils.api_init import pgw
from utils.api_init import xpaas
import pandas as pd
import numpy as np
import time
import math
import json


class loggerSpClass:
    logCount = 0

    def printLog(self, ins_str):
        logger.info(f"[SYSTEM-INFO] {ins_str}")
        self.logCount += 1

    def printLogReport(self, ins_str):
        logger.info(f"[OUTPUT-REPORT] {ins_str}")
        self.logCount += 1

    def printLogSummary(self, ins_str):
        logger.info(f"[SUMMARY-REPORT] {ins_str}")
        self.logCount += 1


logVar = loggerSpClass()

logVar.printLog(f"pandas version is " + pd.__version__)
logVar.printLog(f"numpy version is " + np.__version__)

# STATIC PARAMETER DEFINITIONS
kpiList = ["DEV_SGNB_ADD_SUCC_RT", "DEV_SGNB_ADD_ATTEMPTS"]

moParameters = {'NSADCMGMTCONFIG': [{"place": "attributes",
                                     "parameter": "LOCALCELLID"
                                     },
                                    {"place": "attributes",
                                     "parameter": "UPPERLAYERINDICATIONSWITCH"
                                     }
                                    ]}

logLimit = int(context.get('LOG_LIMIT'))
batchSize = int(context.get('BATCH_SIZE'))
backLogDuration = context.get('BACKLOG_DURATION')
targetCluster = context.get('NAAS_CLUSTER')
srThreshold = int(context.get('MIN_REQ_SR_THRESHOLD'))
attThreshold = int(context.get('MIN_REQ_ATTEMPT_THRESHOLD'))
maxNumberOfAction = int(context.get('ACTION_LIMIT'))
work_items = []

logVar.printLog(f"UI VARIABLES: LOG_LIMIT IS {logLimit}")
logVar.printLog(f"UI VARIABLES: NAAS_CLUSTER IS {targetCluster}")
logVar.printLog(f"UI VARIABLES: PROVISION_MODE IS {context.get('PROVISION_MODE')}")
logVar.printLog(f"UI VARIABLES: BACKLOG_DURATION IS {backLogDuration}")
logVar.printLog(f"UI VARIABLES: BATCH_SIZE IS {batchSize}")
logVar.printLog(f"UI VARIABLES: MIN_REQ_SR_THRESHOLD IS {srThreshold}")
logVar.printLog(f"UI VARIABLES: MIN_REQ_ATTEMPT_THRESHOLD IS {attThreshold}")
logVar.printLog(f"UI VARIABLES: ACTION_LIMIT IS {maxNumberOfAction}")


# COMMON FUNCTIONS
def generateReport(dataFrame, prefix):
    logVar.printLogReport(f'#{prefix}#{"#".join(dataFrame.keys().tolist())}')

    currentLogRow = logVar.logCount
    remaining_row_count = max(logLimit - 100 - currentLogRow, 1)
    total_cell_count = len(dataFrame.values.tolist())
    cell_per_line = math.floor(total_cell_count / remaining_row_count)

    logVar.printLog(f"currentLogRow -> {currentLogRow}")
    logVar.printLog(f"remaining_row_count -> {remaining_row_count}")
    logVar.printLog(f"total_cell_count -> {total_cell_count}")
    logVar.printLog(f"cell_per_line -> {cell_per_line}")

    rowCounter = 0

    str_line = []
    cell_count_in_line = 0

    for eachRow in dataFrame.values.tolist():

        rowCounter = rowCounter + 1
        for ii in range(len(eachRow)):
            if str(eachRow[ii].__class__.__name__) != "str":
                eachRow[ii] = str(eachRow[ii])

        cell_count_in_line = cell_count_in_line + 1
        str_line.append("#".join(eachRow))

        if cell_count_in_line == cell_per_line or rowCounter == len(dataFrame.values.tolist()):

            logVar.printLogReport(f'#{prefix}#{"####".join(str_line)}')
            cell_count_in_line = 0
            str_line = []


def elapsedTimeMeasure(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        logVar.printLog(f"Elapsed time for {method.__name__} is {round(te - ts, 2)} sec")
        return result

    return timed


def convertToPdFrame(lst):
    logVar.printLog(f"Total number of pandas object is {len(lst)}")
    lst = list(set(lst))
    lst = pd.DataFrame([t.__dict__ for t in lst])
    return lst


@elapsedTimeMeasure
def joinTwoListWithSingleAttribute(lst1, lst2, attribute):
    return pd.merge(lst1, lst2, on=attribute, how='left')


@elapsedTimeMeasure
def joinTwoListWithMultipleAttribute(lst1, lst2, left_on, right_on):
    return pd.merge(lst1, lst2, how='left', left_on=left_on, right_on=right_on)


def printResponseDetails(page_info):
    logVar.printLog(f"Total element size is {page_info['numberOfElements']}")
    logVar.printLog(f"Total required request count is {page_info['numberOfPages']}")


def getNextPageUrl(page_info):
    if page_info['currentPage'] == page_info['numberOfPages']:
        return {'EOF': True}
    else:
        a1 = page_info['links']
        a2 = a1[0]
        return {'EOF': False, 'URL': a2['href']}

    # NAAS RELATED OBJECTS & METHODS


class cellObject:
    def __init__(self, abstractId, cellName, guid):
        self.abstractId = abstractId
        self.cellName = cellName
        self.guid = guid


class cellMo:
    def __init__(self, guid, eNodeBId, LocalCellId, uid, parent_uid, paramSet):
        self.guid = guid
        self.eNodeBId = eNodeBId
        self.LocalCellId = LocalCellId
        self.uid = uid
        self.parent_uid = parent_uid
        self.cell_paramSet = paramSet


class childMo:
    def __init__(self, childMo_uid, childMo_parent_uid, paramSet):
        self.childMo_uid = childMo_uid
        self.childMo_parent_uid = childMo_parent_uid
        self.paramSet = paramSet


def populateCellMoList(lst, jsonFmt, params):
    for eachMoObj in jsonFmt['elements']:
        eachMo = eachMoObj['managedObject']
        dicts = {}
        for eachParam in params:
            try:
                dicts[eachParam.get('parameter')] = eachMo.get(eachParam.get('place')).get(eachParam.get('parameter'))
            except:
                dicts[eachParam.get('parameter')] = None

        lst.append(cellMo(guid=eachMo['guid'],
                          eNodeBId=eachMo.get('meta').get('ENODEBID'),
                          LocalCellId=eachMo.get('attributes').get('LOCALCELLID'),
                          uid=eachMo['uid'],
                          parent_uid=eachMo['parent_uid'],
                          paramSet=dicts))


def populateChildMoList(lst, jsonFmt, params):
    try:
        jsonFmt['elements']
    except:
        logVar.printLog(f"populateChildMoList.elements is missing")
        return None

    for eachMoObj in jsonFmt['elements']:
        try:
            eachMo = eachMoObj['managedObject']
        except:
            logVar.printLog(f"populateChildMoList.managedObject is missing")
            continue
        dicts = {}
        for eachParam in params:
            try:
                dicts[eachParam.get('parameter')] = eachMo.get(eachParam.get('place')).get(eachParam.get('parameter'))
            except:
                dicts[eachParam.get('parameter')] = None

        lst.append(childMo(childMo_uid=eachMo['uid'],
                           childMo_parent_uid=eachMo['parent_uid'],
                           paramSet=dicts))


def getNaasMoFromURL(url):
    split_str = url.split("?")
    split_str = split_str[1].split("&")

    paramSet = {'continuationId': None, 'links': None}

    for each in split_str:
        each_str = each.split("=")
        paramSet[each_str[0]] = each_str[1]

    logVar.printLog(paramSet)
    response = naas.api.mos.find_mos(params=paramSet).body
    return response


@elapsedTimeMeasure
def getMosFromNaas(moName, baseMoList):
    inst_list = []
    try:
        desiredParams = moParameters[moName]
    except:
        desiredParams = {}

    if moName == "CELL":
        criteria = "guid"
    else:
        criteria = "parent_uid"

    criteria_values_in_list = list(set([f"\"{baseMoList.loc[ii, criteria]}\"" for ii in range(len(baseMoList))]))
    criteria_values = ",".join(criteria_values_in_list)
    criteria_values = criteria_values[1:-1]

    post_message = {"class": f"{moName}",
                    criteria: [criteria_values]}

    post_message = str(post_message).replace("'", "\"")
    response = naas.api.mos.find_mos(body=json.loads(post_message), params={'links': 'false'}).body

    if moName == "CELL":
        populateCellMoList(lst=inst_list, jsonFmt=response, params=desiredParams)
    else:
        populateChildMoList(lst=inst_list, jsonFmt=response, params=desiredParams)

    pagination = response['pagination']
    printResponseDetails(page_info=pagination)

    nextPageInfo = getNextPageUrl(page_info=pagination)

    while not nextPageInfo['EOF']:

        response = getNaasMoFromURL(url=nextPageInfo['URL'])

        if moName == "CELL":
            populateCellMoList(lst=inst_list, jsonFmt=response, params=desiredParams)
        else:
            populateChildMoList(lst=inst_list, jsonFmt=response, params=desiredParams)

        nextPageInfo = getNextPageUrl(page_info=response['pagination'])

    if len(inst_list) == 0:
        if moName == "CELL":
            inst_list.append(cellMo(guid=None, eNodeBId=None, LocalCellId=None, uid=None, parent_uid=None, paramSet={}))
        else:
            inst_list.append(childMo(childMo_uid=None, childMo_parent_uid=None, paramSet={}))

    return convertToPdFrame(lst=inst_list)


def getNaasFromURL(url):
    split_str = url.split("?")
    split_str = split_str[1].split("&")

    paramSet = {'fields': None, 'continuationId': None, 'includeExtensions': None, 'links': None}

    for each in split_str:
        each_str = each.split("=")
        paramSet[each_str[0]] = each_str[1]

    logVar.printLog(paramSet)
    response = naas.api.clusters.get_cluster_cells(targetCluster, params=paramSet).body
    return response


def populateCellList(lst, jsonFmt):
    for eachCellObj in jsonFmt['elements']:
        eachCell = eachCellObj['cell']

        lst.append(cellObject(abstractId=eachCell['_id'],
                              cellName=eachCell['name'],
                              guid=eachCell['guid']))


@elapsedTimeMeasure
def getTargetCells():
    cellList = []
    response = naas.api.clusters.get_cluster_cells(targetCluster, params={'fields': '_id,name,guid'}).body

    populateCellList(lst=cellList, jsonFmt=response)

    pagination = response['pagination']
    printResponseDetails(page_info=pagination)

    nextPageInfo = getNextPageUrl(page_info=pagination)

    while not nextPageInfo['EOF']:
        response = getNaasFromURL(url=nextPageInfo['URL'])
        populateCellList(lst=cellList, jsonFmt=response)

        nextPageInfo = getNextPageUrl(page_info=response['pagination'])

    return convertToPdFrame(cellList)


def extractLocalCellIdInfo(dataFrame):
    for ii in range(len(dataFrame)):
        dataFrame.loc[ii, 'childMo_LocalCellId'] = dataFrame.loc[ii, 'paramSet'].get('LOCALCELLID')


# XPAAS RELATED OBJECTS & METHODS

class pmObject:
    def __init__(self, abstractId, kpis):
        self.abstractId = abstractId
        self.kpis = kpis


def populatePmList(lst, jsonFmt):
    try:
        jsonFmt['elements']
    except:
        logVar.printLog(f"populatePmList.elements is missing")
        return None

    for eachCellObj in jsonFmt['elements']:
        try:
            dataPoint = eachCellObj['data_points']
            if len(dataPoint) != 1:
                logVar.printLog(f"populatePmList.dataPoint.size is {len(dataPoint)}")
                logVar.printLog(dataPoint)

            dataPoint_ = dataPoint[0]
            try:
                values = dataPoint_['values']
                dicts = {}
                for eachCounter in kpiList:
                    try:
                        dicts[eachCounter] = values.get(eachCounter).get("value")
                    except:
                        dicts[eachCounter] = None

                lst.append(pmObject(abstractId=eachCellObj['_cellId'],
                                    kpis=dicts))
            except:
                logVar.printLog(f"populatePmList.values is missing")
        except:
            logVar.printLog(f"populatePmList.data_points is missing")


@elapsedTimeMeasure
def getTargetPmData(cellList):
    kpiStr = ",".join(f"\"{x}\"" for x in kpiList)
    kpiStr = kpiStr[1:-1]
    pmList = []

    batchCount = math.ceil(len(cellList) / batchSize)
    logVar.printLog(f"Required batch count is {batchCount} to get {len(cellList)} cell data")

    for ii in range(batchCount):
        logVar.printLog(f"PM Set Batch {ii + 1} is procedeed")

        minIdx = int(batchSize * ii)
        maxIdx = min(int(batchSize * (ii + 1)), len(cellList))

        abstractIdStr = ",".join([f"\"{cellList.loc[ii, 'abstractId']}\"" for ii in range(minIdx, maxIdx)])
        abstractIdStr = abstractIdStr[1:-1]
        post_message = {"aggregatePopulation": "false",
                        "backlog": backLogDuration,
                        "kpiNames": [kpiStr],
                        "population": [abstractIdStr]
                        }

        post_message = str(post_message).replace("'", "\"")
        response = xpaas.api.kpis.get_kpi_data(body=json.loads(post_message), params={'per_page': batchSize}).body
        populatePmList(pmList, response)

        # TODO: NOT TESTED PART
        pagination = response['pagination']
        printResponseDetails(page_info=pagination)
        nextPageInfo = getNextPageUrl(page_info=pagination)

        if not nextPageInfo['EOF']:
            logVar.printLog("There is a pagination on XPaaS request. Re-format the size.")

    if len(pmList) == 0:
        pmList.append(pmObject(abstractId=None, kpis={}))

    return convertToPdFrame(lst=pmList)


stateTable = {'KPI_DATA_IS_NOT_AVILABLE': 0, 'KPI_DATA_IS_NOT_ENOUGH': 0, 'GOOD_STATE': 0, 'BAD_STATE': 0}
actionTable = {'SET_TO_1': 0, 'SET_TO_0': 0}
listOfMosWithAction = []


def getStatesAccordingToPM(dataFrame):
    action_count = 0
    for idx in range(len(dataFrame)):

        try:
            DEV_SGNB_ADD_SUCC_RT = dataFrame.loc[idx, 'kpis'].get('DEV_SGNB_ADD_SUCC_RT')
            DEV_SGNB_ADD_ATTEMPTS = dataFrame.loc[idx, 'kpis'].get('DEV_SGNB_ADD_ATTEMPTS')
        except:
            DEV_SGNB_ADD_SUCC_RT = None
            DEV_SGNB_ADD_ATTEMPTS = None

        try:
            UPPERLAYERINDICATIONSWITCH = str(dataFrame.loc[idx, 'paramSet'].get('UPPERLAYERINDICATIONSWITCH'))
        except:
            dataFrame.loc[idx, 'PM_STATE'] = "NOT_CHECKED"
            dataFrame.loc[idx, 'DECISION'] = "MISSING_CM"
            continue

        if (int(DEV_SGNB_ADD_ATTEMPTS) if DEV_SGNB_ADD_ATTEMPTS is not None else None) == 0:
            dataFrame.loc[idx, 'PM_STATE'] = "KPI_DATA_IS_NOT_ENOUGH"
            # dataFrame.loc[idx, 'DECISION'] = 'NONE' -- CHANGED AT 07-OCT-2022
            stateTable['KPI_DATA_IS_NOT_ENOUGH'] = stateTable['KPI_DATA_IS_NOT_ENOUGH'] + 1

            # ADDED AT 07-OCT-2022
            if UPPERLAYERINDICATIONSWITCH == '0':
                dataFrame.loc[idx, 'DECISION'] = 'ALREADY-DISABLED'

            else:
                dataFrame.loc[idx, 'DECISION'] = 'DISABLED-BY-DEV'
                if action_count < maxNumberOfAction or maxNumberOfAction == -1:

                    if dataFrame.loc[idx, 'childMo_uid'] not in listOfMosWithAction:
                        listOfMosWithAction.append(dataFrame.loc[idx, 'childMo_uid'])
                        work_items.append({
                            'type': 'CHANGE_SPECIFIC_PARAMETER',
                            '_moId': dataFrame.loc[idx, 'childMo_uid'],
                            'parameterName': 'UPPERLAYERINDICATIONSWITCH',
                            'value': "0"
                        })
                        action_count = action_count + 1
                        actionTable['SET_TO_0'] = actionTable['SET_TO_0'] + 1
                    else:
                        dataFrame.loc[idx, 'DECISION'] = 'DUPLICATED_MO'

        elif DEV_SGNB_ADD_SUCC_RT is None or DEV_SGNB_ADD_ATTEMPTS is None:
            dataFrame.loc[idx, 'PM_STATE'] = "KPI_DATA_IS_NOT_AVILABLE"
            dataFrame.loc[idx, 'DECISION'] = 'NONE'
            stateTable['KPI_DATA_IS_NOT_AVILABLE'] = stateTable['KPI_DATA_IS_NOT_AVILABLE'] + 1

        elif DEV_SGNB_ADD_ATTEMPTS < attThreshold:
            dataFrame.loc[idx, 'PM_STATE'] = "KPI_DATA_IS_NOT_ENOUGH"
            # dataFrame.loc[idx, 'DECISION'] = 'NONE' -- CHANGED AT 07-OCT-2022
            stateTable['KPI_DATA_IS_NOT_ENOUGH'] = stateTable['KPI_DATA_IS_NOT_ENOUGH'] + 1

            # ADDED AT 07-OCT-2022
            if UPPERLAYERINDICATIONSWITCH == '0':
                dataFrame.loc[idx, 'DECISION'] = 'ALREADY-DISABLED'
            else:
                dataFrame.loc[idx, 'DECISION'] = 'DISABLED-BY-DEV'
                if action_count < maxNumberOfAction or maxNumberOfAction == -1:

                    if dataFrame.loc[idx, 'childMo_uid'] not in listOfMosWithAction:
                        listOfMosWithAction.append(dataFrame.loc[idx, 'childMo_uid'])
                        work_items.append({
                            'type': 'CHANGE_SPECIFIC_PARAMETER',
                            '_moId': dataFrame.loc[idx, 'childMo_uid'],
                            'parameterName': 'UPPERLAYERINDICATIONSWITCH',
                            'value': "0"
                        })
                        action_count = action_count + 1
                        actionTable['SET_TO_0'] = actionTable['SET_TO_0'] + 1
                    else:
                        dataFrame.loc[idx, 'DECISION'] = 'DUPLICATED_MO'

        elif DEV_SGNB_ADD_SUCC_RT > srThreshold:
            dataFrame.loc[idx, 'PM_STATE'] = "GOOD_STATE"
            stateTable['GOOD_STATE'] = stateTable['GOOD_STATE'] + 1

            if UPPERLAYERINDICATIONSWITCH == "1":
                dataFrame.loc[idx, 'DECISION'] = 'ALREADY-ENABLED'
            else:
                dataFrame.loc[idx, 'DECISION'] = 'ENABLED-BY-DEV'
                if action_count < maxNumberOfAction or maxNumberOfAction == -1:

                    if dataFrame.loc[idx, 'childMo_uid'] not in listOfMosWithAction:
                        listOfMosWithAction.append(dataFrame.loc[idx, 'childMo_uid'])
                        work_items.append({
                            'type': 'CHANGE_SPECIFIC_PARAMETER',
                            '_moId': dataFrame.loc[idx, 'childMo_uid'],
                            'parameterName': 'UPPERLAYERINDICATIONSWITCH',
                            'value': "1"
                        })
                        action_count = action_count + 1
                        actionTable['SET_TO_1'] = actionTable['SET_TO_1'] + 1
                    else:
                        dataFrame.loc[idx, 'DECISION'] = 'DUPLICATED_MO'
        else:
            dataFrame.loc[idx, 'PM_STATE'] = "BAD_STATE"
            stateTable['BAD_STATE'] = stateTable['BAD_STATE'] + 1

            if UPPERLAYERINDICATIONSWITCH == '0':
                dataFrame.loc[idx, 'DECISION'] = 'ALREADY-DISABLED'
            else:
                dataFrame.loc[idx, 'DECISION'] = 'DISABLED-BY-DEV'
                if action_count < maxNumberOfAction or maxNumberOfAction == -1:

                    if dataFrame.loc[idx, 'childMo_uid'] not in listOfMosWithAction:
                        listOfMosWithAction.append(dataFrame.loc[idx, 'childMo_uid'])
                        work_items.append({
                            'type': 'CHANGE_SPECIFIC_PARAMETER',
                            '_moId': dataFrame.loc[idx, 'childMo_uid'],
                            'parameterName': 'UPPERLAYERINDICATIONSWITCH',
                            'value': "0"
                        })
                        action_count = action_count + 1
                        actionTable['SET_TO_0'] = actionTable['SET_TO_0'] + 1
                    else:
                        dataFrame.loc[idx, 'DECISION'] = 'DUPLICATED_MO'


def main():
    # PHASE.1 DEFINE REQUIRED PM DATA
    post_message = {"description": "SgNB addition attempts",
                    "formulas": [
                        {
                            "draft": "false",
                            "formula": "#L_NsaDc_SgNB_Add_Att",
                            "vendor": "HUAWEI"
                        },
                        {
                            "draft": "false",
                            "formula": "#SGNB_ADD_PREP_ATT",
                            "vendor": "NOKIA"
                        }
                    ],
                    "name": "DEV_SGNB_ADD_ATTEMPTS",
                    "technology": "LTE",
                    "units": "#"
                    }

    post_message = str(post_message).replace("'", "\"")
    response = xpaas.api.kpis.create_kpi(body=json.loads(post_message)).body

    logVar.printLog(f"KPI GENERATION FOR DEV_SGNB_ADD_ATTEMPTS -> {response}")

    post_message = {"description": "SgNB addition success ratio",
                    "formulas": [
                        {
                            "draft": "false",
                            "formula": "100*#L_NsaDc_SgNB_Add_Succ/#L_NsaDc_SgNB_Add_Att",
                            "vendor": "HUAWEI"
                        },
                        {
                            "draft": "false",
                            "formula": "100*#SGNB_ADD_PREP_SUCC/#SGNB_ADD_PREP_ATT",
                            "vendor": "NOKIA"
                        }
                    ],
                    "name": "DEV_SGNB_ADD_SUCC_RT",
                    "technology": "LTE",
                    "units": "#"
                    }

    post_message = str(post_message).replace("'", "\"")
    response = xpaas.api.kpis.create_kpi(body=json.loads(post_message)).body

    logVar.printLog(f"KPI GENERATION FOR DEV_SGNB_ADD_SUCC_RT -> {response}")

    # PHASE.2 GET NAAS RELATED DATA
    targetCellList = getTargetCells()

    cellMoList = getMosFromNaas(moName="CELL", baseMoList=targetCellList)

    NsaDcMgmtConfigList = getMosFromNaas(moName="NSADCMGMTCONFIG", baseMoList=cellMoList)
    extractLocalCellIdInfo(NsaDcMgmtConfigList)

    targetCellList = joinTwoListWithSingleAttribute(lst1=targetCellList, lst2=cellMoList, attribute='guid')
    del cellMoList

    targetCellList = joinTwoListWithMultipleAttribute(lst1=targetCellList, lst2=NsaDcMgmtConfigList, left_on=['LocalCellId', 'parent_uid'], right_on=['childMo_LocalCellId', 'childMo_parent_uid'])
    del NsaDcMgmtConfigList

    kpiDataList = getTargetPmData(targetCellList)
    targetCellList = joinTwoListWithSingleAttribute(lst1=targetCellList, lst2=kpiDataList, attribute='abstractId')
    del kpiDataList
    getStatesAccordingToPM(targetCellList)

    # filtered_values = np.where((targetCellList['DECISION'] == 'DISABLED-BY-DEV') | (targetCellList['DECISION'] == 'ENABLED-BY-DEV'))
    # targetCellList = targetCellList.loc[filtered_values]

    logVar.printLogSummary(f"actionTable -> {actionTable}")
    logVar.printLogSummary(f"stateTable -> {stateTable}")

    if len(work_items) > 0:
        if context.get('PROVISION_MODE') in ["OFFLINE_SIM", "ONLINE_SIM", "OPERATIONAL"]:

            work_order = {
                'description': "UPDATING NSADCMGMTCONFIG.UPPERLAYERINDICATIONSWITCH",
                'mode': context.get('PROVISION_MODE'),
                'method': 'NON_TRANSACTION',
                'priority': '1',
                'trackingId': context.get('TRACKING_ID'),
                'workItems': work_items
            }

            logVar.printLog(f"context.get('TRACKING_ID') -> {context.get('TRACKING_ID')}")
            _ = pgw.api.workorders.send_workorder(body=work_order)

        else:
            logVar.printLog(f"No PGW due to {context.get('PROVISION_MODE')}")
    else:
        logVar.printLog("No cells meeting criteria for optimization")

    if len(targetCellList):
        generateReport(dataFrame=targetCellList, prefix="targetCellList")


if __name__ == '__main__':
    main()
