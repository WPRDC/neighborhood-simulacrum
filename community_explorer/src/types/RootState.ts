import { TopBarState } from 'app/containers/TopBar/types';
import { ExplorerState } from 'app/containers/Explorer/types';
import { DataVizState } from 'app/containers/DataViz/types';
// [IMPORT NEW CONTAINERSTATE ABOVE] < Needed for generating containers seamlessly

/* 
  Because the redux-injectors injects your reducers asynchronously somewhere in your code
  You have to declare them here manually
*/
export interface RootState {
  topBar?: TopBarState;
  explorer?: ExplorerState;
  dataViz?: DataVizState;
  // [INSERT NEW REDUCER KEY ABOVE] < Needed for generating containers seamlessly
}
