/**
 *
 * DataViz
 *
 */

import React, { Ref, RefObject, useRef } from 'react';
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
import { getSpecificDataViz } from './util';

import {
  DataVizBase,
  DataVizData,
  DataVizID,
  VariableSource,
  VizProps,
} from '../../types';
import { ProgressBar } from '@react-spectrum/progress';
import styled from 'styled-components/macro';
import { selectColorMode } from '../GlobalSettings/selectors';
import { DOMRefValue, ViewStyleProps } from '@react-types/shared';
import { DataVizVariant } from './types';
import Measure from 'react-measure';

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

  /* Keep track fo dimensions to send to vega charts */
  const [{ width, height }, setDimensions] = React.useState({
    width: 0,
    height: 0,
  });

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
  const { name, description } = dataViz || {};

  // get correct component
  const CurrentViz:
    | React.FunctionComponent<VizProps<DataVizBase, DataVizData>>
    | undefined = getSpecificDataViz(dataViz);

  // get variant props
  const wrapperProps = getVizWrapperProps(variant);

  return (
    <>
      <Measure
        bounds
        onResize={contentRect => {
          if (contentRect.bounds) setDimensions(contentRect.bounds);
        }}
      >
        {({ measureRef }) => (
          <div ref={measureRef}>
            <View aria-label="data presentation preview" {...wrapperProps}>
              {!!CurrentViz && (
                <CurrentViz
                  dataViz={dataViz}
                  colorScheme={colorScheme}
                  vizHeight={height - 15}
                  vizWidth={width - 35}
                />
              )}
            </View>
          </div>
        )}
      </Measure>
      <View paddingTop="size-50">
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
      </View>
    </>
  );
}

DataViz.defaultProps = {
  variant: DataVizVariant.Default,
};

function getVizWrapperProps(variant: DataVizVariant): Partial<ViewStyleProps> {
  switch (variant) {
    case DataVizVariant.Preview:
      return {
        padding: 'size-100',
        minHeight: 'size-2400',
        overflow: 'auto',
      };
    case DataVizVariant.Blurb:
      return {};
    case DataVizVariant.Default:
    default:
      return {
        borderWidth: 'thick',
        backgroundColor: 'gray-100',
        borderRadius: 'small',
        minHeight: 'size-3600',
        marginX: 'size-100',
        margin: 'size-100',
      };
  }
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

const List = styled.ul`
  padding-left: 1rem;
  margin-top: 2px;
  list-style: none;
`;
