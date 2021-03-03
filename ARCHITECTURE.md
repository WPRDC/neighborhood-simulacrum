# Conceptual Framework


## Primary Components

### Variable
_A piece of information that describes geographies at points in time._

`Variables` handle the extraction and presentation data.  
`Variables` connect to source data through `Sources`.
`Variables` my have different `sources`

Under the hood, there are two types of `Variables`: `CensusVariable` and `CKANVariable` that differ only in how they extract data.

**Properties**
 - style/presentation options (common)
 - data extraction options (subclass specific)
 - data sources (subclass specific)


#### Census Variable
_A subclass of `Variable` that that use ACS or Census tables to generate values. It connects to said data through `CensusSources`._  

A complete collection of `CensusVariables` is generated through scripts.

#### CKAN Variable
_A subclass of `Variable` that uses connection to CKAN, through `CKANSources`, to generate values._

We might be able to automatically generate these as well. At some point

### Source
_A connection to a source dataset_

`Sources` handle connecting to source data.

**Properties**
 - time coverage information (range, granularity)
 - connection options (subclass specific)

#### Census Source
_A subclass of `Source` that connects to ACS or Census data._

#### CKAN Source
_A subclass of `Source` that connects to CKAN datasets._

### Time Axis
_A cartesian axis with points representing a point in time._

**Properties**
 - unit of granularity (daily, hourly, etc)
 - axis generation options (subclass-specific)

#### Static Time Axis
_A `TimeAxis` Defined with a hardcoded array of time points._

#### Static Consecutive Time Axis
_A `TimeAxis` defined with terminal timepoints and number of ticks._

Three variants
* only `start` time: starts at `start` and continues forward in time for `ticks` ticks 
* only `end` time: starts at `end` - `ticks` * `unit` and continues for `ticks` ticks to end at `end` 
* both provided: starts at `start` and continues to `end` with as many ticks spaced by `unit` as necessary


#### Relative Time Axis
`TimeAxis` that is generated ad hoc based on the current time at calculation.
(e.g. The past 3 days)


### Data Presentation
_A way to present data._

* visualizations
* maps  
* text-based social media (tweets, reddit bot)
* email alerts
* phone calls