/**
 *
 * DataViz
 *
 */

import React from 'react';
import { useDispatch, useSelector } from 'react-redux';

import { useInjectReducer, useInjectSaga } from 'utils/redux-injectors';
import { actions, reducer, sliceKey } from './slice';
import { dataVizSaga } from './saga';
import { makeSelectDataVizData } from './selectors';
import { selectSelectedGeogIdentifier } from '../Explorer/selectors';
import { getSpecificDataViz, getVariantComponent } from './util';

import Download from '@spectrum-icons/workflow/DataDownload';
import Share from '@spectrum-icons/workflow/Share';
import Report from '@spectrum-icons/workflow/AlertCircleFilled';

import {
  DataVizBase,
  DataVizData,
  DataVizID,
  Domain,
  Indicator,
  Subdomain,
  Taxonomy,
  URLNavParams,
  VizMenuItem,
  VizProps,
} from '../../types';
import { selectColorMode } from '../GlobalSettings/selectors';
import { AvailableDialogs, DataVizVariant, MenuItem } from './types';
import { DataVizMenu } from './DataVizMenu';
import { DialogContainer, Heading, Item } from '@adobe/react-spectrum';
import { UserReportDialog } from '../../components/UserReportDialog';
import { ShareDialog } from '../../components/ShareDialog';
import { useHistory, useLocation, useParams } from 'react-router-dom';

interface Props {
  dataVizID: DataVizID;
  variant: DataVizVariant;
  taxonomy?: Taxonomy;
}

export function DataViz(props: Props) {
  const { dataVizID, variant, taxonomy } = props;
  useInjectReducer({ key: sliceKey, reducer: reducer });
  useInjectSaga({ key: sliceKey, saga: dataVizSaga });

  const location = useLocation();
  const history = useHistory();
  const dispatch = useDispatch();

  const {
    domainSlug,
    subdomainSlug,
    indicatorSlug,
  } = useParams<URLNavParams>();

  const taxonomyItems = getTaxonomyItems(
    taxonomy,
    domainSlug,
    subdomainSlug,
    indicatorSlug,
  );

  /* Instance state */
  const geogIdentifier = useSelector(selectSelectedGeogIdentifier);
  const selectDataVizDataRecord = React.useMemo(makeSelectDataVizData, []);
  const dataVizDataRecord = useSelector(state =>
    selectDataVizDataRecord(state, { dataVizID: dataVizID }),
  );
  const colorScheme = useSelector(selectColorMode);

  const [openDialog, setOpenDialog] = React.useState<AvailableDialogs | null>(
    null,
  );

  function handleMenuSelection(key: React.Key): void {
    switch (key as VizMenuItem) {
      case VizMenuItem.DownloadData:
        dispatch(actions.downloadDataVizData(dataViz));
        break;
      case VizMenuItem.DownloadSVG:
        // todo: use vega svg download
        break;
      case VizMenuItem.Share:
        setOpenDialog(AvailableDialogs.Share);
        break;
      case VizMenuItem.Report:
        setOpenDialog(AvailableDialogs.Report);
        break;
    }
  }

  function handleExplore() {
    const path = location.pathname;
    history.push(path + `/${dataVizID.slug}`);
  }

  const menuItems: MenuItem[] = [
    {
      key: VizMenuItem.DownloadData,
      label: 'Download Data',
      icon: <Download size="S" />,
    },
    { key: VizMenuItem.Share, label: 'Share...', icon: <Share size="S" /> },
    { key: VizMenuItem.Report, label: 'Report...', icon: <Report size="S" /> },
  ];

  // when this badboy renders, we need to get its data.
  React.useEffect(() => {
    const hasData = !!dataVizDataRecord && !!dataVizDataRecord.dataViz;
    if (!!geogIdentifier && !hasData) {
      dispatch(
        actions.requestDataViz({ dataVizID, geogIdentifier: geogIdentifier }),
      );
    }
  }, [geogIdentifier]);

  // if the record for this viz doesn't exist somehow, gtfo
  // fixme: is this even possible? can these be addressed through better typing?
  if (!dataVizDataRecord) return null;

  /* Extracting (meta)data from the dataviz */
  const { isLoading, error, dataViz } = dataVizDataRecord;
  if (error) console.warn(error);

  // get correct component for the viz
  const CurrentViz:
    | React.FC<VizProps<DataVizBase, DataVizData>>
    | undefined = getSpecificDataViz(dataViz, error);

  // variant controls the contents and style of component around the actual dataviz
  const WrapperComponent = getVariantComponent(variant);

  const breadcrumbs = getBreadCrumbs(taxonomyItems, dataVizID);

  return (
    <>
      <WrapperComponent
        dataViz={dataViz}
        geogIdentifier={geogIdentifier}
        CurrentViz={CurrentViz}
        colorScheme={colorScheme}
        isLoading={isLoading}
        breadcrumbs={breadcrumbs}
        onExplore={handleExplore}
        error={error}
        menu={
          <DataVizMenu
            menuItems={menuItems}
            onMenuItemClick={handleMenuSelection}
          />
        }
      />
      <DialogContainer onDismiss={() => null}>
        {openDialog === AvailableDialogs.Report && (
          <UserReportDialog
            onClose={() => setOpenDialog(null)}
            dataVizID={dataVizID}
          />
        )}
        {openDialog === AvailableDialogs.Share && !!dataViz && (
          <ShareDialog onClose={() => setOpenDialog(null)} dataViz={dataViz} />
        )}
      </DialogContainer>
    </>
  );
}

DataViz.defaultProps = {
  variant: DataVizVariant.Default,
};

function getTaxonomyItems(
  taxonomy?: Taxonomy,
  domainSlug?: string,
  subdomainSlug?: string,
  indicatorSlug?: string,
): { domain?: Domain; subdomain?: Subdomain; indicator?: Indicator } {
  const domain =
    !!taxonomy && !!domainSlug
      ? taxonomy.find(d => d.slug === domainSlug)
      : undefined;
  const subdomain =
    !!domain && !!subdomainSlug
      ? domain.subdomains.find(sd => sd.slug === subdomainSlug)
      : undefined;
  const indicator =
    !!subdomain && !!indicatorSlug
      ? subdomain.indicators.find(i => i.slug === indicatorSlug)
      : undefined;
  return { domain, subdomain, indicator };
}

function getBreadCrumbs(
  items: {
    domain?: Domain;
    subdomain?: Subdomain;
    indicator?: Indicator;
  },
  dataViz: DataVizID,
) {
  const { domain, subdomain, indicator } = items;
  const path = [domain, subdomain, indicator].reduce(
    (filtered: JSX.Element[], item) => {
      return !!item
        ? [...filtered, <Item key={item.slug}>{item.name}</Item>]
        : filtered;
    },
    [],
  );
  return [
    ...path,
    <Item key={dataViz.slug}>
      <Heading
        level={3}
        margin="size-100"
        marginTop-="size-0"
        UNSAFE_style={{ fontSize: '2rem' }}
      >
        {dataViz.name}
      </Heading>
    </Item>,
  ];
}
