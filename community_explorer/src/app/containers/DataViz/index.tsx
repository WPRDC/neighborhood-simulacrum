/**
 *
 * DataViz
 *
 */

import React from 'react';
import { useSelector, useDispatch } from 'react-redux';

import { useInjectReducer, useInjectSaga } from 'utils/redux-injectors';
import { reducer, sliceKey } from './slice';
import { actions } from './slice';
import { dataVizSaga } from './saga';
import { View } from '@react-spectrum/view';
import { makeSelectDataVizData } from './selectors';
import { selectSelectedRegionDescriptor } from '../Explorer/selectors';
import { getSpecificDataViz } from './util';

import { DataVizID } from '../../types';
import { Text } from '@adobe/react-spectrum';
import { ProgressBar } from '@react-spectrum/progress';
import { Flex } from '@react-spectrum/layout';

interface Props {
  dataVizID: DataVizID;
}

export function DataViz(props: Props) {
  const { dataVizID } = props;
  useInjectReducer({ key: sliceKey, reducer: reducer });
  useInjectSaga({ key: sliceKey, saga: dataVizSaga });

  const dispatch = useDispatch();

  /* Instance state */
  const regionDescriptor = useSelector(selectSelectedRegionDescriptor);
  const selectDataVizDataRecord = React.useMemo(makeSelectDataVizData, []);
  const dataVizDataRecord = useSelector(state =>
    selectDataVizDataRecord(state, { dataVizID: dataVizID }),
  );

  // when this badboy renders, we need to get its data.
  React.useEffect(() => {
    const hasData = !!dataVizDataRecord && !!dataVizDataRecord.dataViz;
    if (!!regionDescriptor && !hasData) {
      dispatch(actions.requestDataViz({ dataVizID, regionDescriptor }));
    }
  }, [regionDescriptor]);

  if (!dataVizDataRecord) return null;

  const { isLoading, error, dataViz } = dataVizDataRecord;

  if (error) console.warn(error);

  return (
    <View>
      {!!dataVizDataRecord && (
        <View maxHeight="size-5000" overflow="auto">
          {isLoading && <LoadingMessage />}
          {!!error && <Text>{dataVizDataRecord.error}</Text>}
          {!!dataViz && getSpecificDataViz(dataViz)}
        </View>
      )}
    </View>
  );
}

const LoadingMessage = () => (
  <Flex alignItems="center" justifyContent="center">
    <View padding="size-200">
      <ProgressBar isIndeterminate label="Loading" />
    </View>
  </Flex>
);
