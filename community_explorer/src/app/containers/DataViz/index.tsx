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

import { DataVizID, VariableSource } from '../../types';
import { Text, Link, Heading, Flex } from '@adobe/react-spectrum';
import { ProgressBar } from '@react-spectrum/progress';
import styled from 'styled-components/macro';

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

  return (
    <View>
      {!!dataVizDataRecord && (
        <View>
          {isLoading && <LoadingMessage />}
          {!!error && <Text>{error}</Text>}
          {!!name && (
            <Heading level={4} UNSAFE_style={{ marginTop: 0 }}>
              {name}
            </Heading>
          )}
          {!!dataViz && getSpecificDataViz(dataViz)}
          {!!sources && <SourceBox sources={sources} />}
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

const SourceBox = ({ sources }: { sources: VariableSource[] }) => (
  <View>
    <View>
      <Text>
        <strong>Sources:</strong>
      </Text>
    </View>
    <List>
      {sources.map(source => (
        <li>
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
