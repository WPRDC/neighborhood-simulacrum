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
  VizMenuItem,
  VizProps,
} from '../../types';
import { selectColorMode } from '../GlobalSettings/selectors';
import { AvailableDialogs, DataVizVariant, MenuItem } from './types';
import { DataVizMenu } from './DataVizMenu';
import { DialogContainer } from '@adobe/react-spectrum';
import { UserReportDialog } from '../../components/UserReportDialog';
import { ShareDialog } from '../../components/ShareDialog';

interface Props {
  dataVizID: DataVizID;
  variant: DataVizVariant;
}

export function DataViz(props: Props) {
  const { dataVizID, variant } = props;
  useInjectReducer({ key: sliceKey, reducer: reducer });
  useInjectSaga({ key: sliceKey, saga: dataVizSaga });

  const dispatch = useDispatch();

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
        console.log('downloadSVG');
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

  const menuItems: MenuItem[] = [
    {
      key: VizMenuItem.DownloadData,
      label: 'Download Data',
      icon: <Download size="S" />,
    },
    { key: VizMenuItem.Share, label: 'Share', icon: <Share size="S" /> },
    { key: VizMenuItem.Report, label: 'Report', icon: <Report size="S" /> },
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
    | undefined = getSpecificDataViz(dataViz);

  // variant controls the contents and style of component around the actual dataviz
  const WrapperComponent = getVariantComponent(variant);

  console.debug({ dataViz });
  return (
    <>
      <WrapperComponent
        dataViz={dataViz}
        geogIdentifier={geogIdentifier}
        CurrentViz={CurrentViz}
        colorScheme={colorScheme}
        isLoading={isLoading}
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
