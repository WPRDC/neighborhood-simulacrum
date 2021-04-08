/**
 *
 * DataViz
 *
 */

import React, { Key } from 'react';
import { useDispatch, useSelector } from 'react-redux';

import { useInjectReducer, useInjectSaga } from 'utils/redux-injectors';
import { actions, reducer, sliceKey } from './slice';
import { dataVizSaga } from './saga';
import {
  ActionButton,
  Flex,
  Heading,
  Link,
  Text,
  View,
} from '@adobe/react-spectrum';
import More from '@spectrum-icons/workflow/More';
import { makeSelectDataVizData } from './selectors';
import { selectSelectedGeogIdentifier } from '../Explorer/selectors';
import {
  downloadChart,
  downloadMiniMap,
  downloadTable,
  getSpecificDataViz,
} from './util';

import {
  ChartData,
  ChartViz,
  DataVizID,
  DataVizResourceType,
  Downloaded,
  MiniMapData,
  MiniMapViz,
  TableData,
  TableViz,
  VariableSource,
} from '../../types';
import { ProgressBar } from '@react-spectrum/progress';
import styled from 'styled-components/macro';
import { DataVizAction } from './types';
import { selectColorMode } from '../GlobalSettings/selectors';

interface Props {
  dataVizID: DataVizID;
  preview?: boolean;
}

export function DataViz(props: Props) {
  const { dataVizID, preview } = props;
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

  // when this badboy renders, we need to get its data.
  React.useEffect(() => {
    const hasData = !!dataVizDataRecord && !!dataVizDataRecord.dataViz;
    if (!!geogIdentifier && !hasData) {
      dispatch(
        actions.requestDataViz({ dataVizID, geogIdentifier: geogIdentifier }),
      );
    }
  }, [geogIdentifier]);

  if (!dataVizDataRecord) return null;

  const { isLoading, error, dataViz } = dataVizDataRecord;

  if (error) console.warn(error);

  const { name, description, variables } = dataViz || {};

  // flatten all the sources attached to variables into one set
  const sources_record =
    variables &&
    variables.reduce(
      (acc, curr) => ({
        ...acc,
        ...curr.sources.reduce((a, c) => ({ ...a, [c.slug]: c }), {}),
      }),
      {} as Record<string, VariableSource>,
    );

  const sources = sources_record && Object.values(sources_record);

  // handle style variations
  const borderWidth = preview ? undefined : 'thin';

  function handleDownload() {
    switch (dataViz.resourcetype) {
      case DataVizResourceType.BarChart:
      case DataVizResourceType.LineChart:
      case DataVizResourceType.PieChart:
        downloadChart(dataViz as Downloaded<ChartViz, ChartData>);
        break;
      case DataVizResourceType.Table:
        downloadTable(dataViz as Downloaded<TableViz, TableData>);
        break;
      case DataVizResourceType.MiniMap:
        downloadMiniMap(dataViz as Downloaded<MiniMapViz, MiniMapData>);
        break;
    }
  }

  function handleMenuClick(actionKey: Key) {
    switch (actionKey) {
      case DataVizAction.Share:
        break;
      case DataVizAction.Embed:
        break;
      case DataVizAction.Download:
        handleDownload();
        break;
      default:
        console.warn(`Unknown action "${actionKey}"`);
    }
  }

  if (!dataVizDataRecord) return <View />;

  return (
    <View
      gridColumn={`auto / span ${!!dataViz ? dataViz.viewWidth : 3}`}
      gridRow={'auto / span 4 '}
      overflow="auto"
      position="relative"
    >
      <View
        padding="size-100"
        aria-label="data presentation preview"
        height="size-3000"
        overflow="auto"
        backgroundColor={preview ? undefined : 'gray-100'}
        borderRadius={preview ? undefined : 'small'}
        marginX={preview ? undefined : 'size-100'}
        margin={preview ? undefined : 'size-100'}
      >
        {!!dataViz && getSpecificDataViz(colorScheme, dataViz)}
      </View>
      <View padding="size-100">
        {isLoading && <LoadingMessage />}
        {!!error && <Text>{error}</Text>}
        {!!name && (
          <Flex>
            <View flexGrow={1}>
              <Heading level={3} UNSAFE_style={{ marginTop: 0 }}>
                {name}
              </Heading>
            </View>
            <View>
              <ActionButton isQuiet>
                <More />
              </ActionButton>
            </View>
          </Flex>
        )}
        {description}
        {!!sources && <SourceBox sources={sources} />}
      </View>
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

const SourceBox = ({ sources }: { sources: VariableSource[] }) => (
  <View>
    <View>
      <Text>Sources:</Text>
    </View>
    <List>
      {sources.map(source => (
        <li key={source.slug}>
          <Link>
            <a href={source.infoLink} target="_blank" rel="noreferrer noopener">
              {source.name}
            </a>
          </Link>
        </li>
      ))}
    </List>
  </View>
);

const HoverActionGroup = styled.div`
  position: absolute;
  right: 0;
  z-index: 1000;
  opacity: 0.3;
  transition: 0.3s;

  &:hover {
    opacity: 1;
  }
`;

const List = styled.ul`
  padding-left: 1rem;
  margin-top: 2px;
  list-style: none;
`;
