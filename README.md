# Watson-Crick Finite Automata analysis module

This is a web app to easily make analysis of Watson-Crick Finite automatas.

The web is available online at: https://wkfa.herokuapp.com/wkfa/

In this website you can upload the specification of a WKFA and convert it to an equivalent 1-limited WKFA. THe app allows you to download that equivalent WKFA and analyze if some word belongs or not to the language recognized by that WKFA, showing the corresponding the trellis. If it's the case, a trace of an acceptation sequence is shown step by step.

It supports normal WKFA along with reverse WKFA and probabilistic WKFA.

The specification of the WKFA must be in a txt file and it's organized in at least 7 lines plus 1 line per transition.
  - The first line must be only "R" if the automata is reverse or "N" if it isn't.
  - The second line must contain only "P" if the automata is probabilistic or "N" if it isn't.
  - The third line contains the alphabet, as a list of symbols separated by commas, e.g. "a,b,c"
  - The fourth line has the complementarity function, as a list of tuples, the two elements of the tuples are separated by commas and the tuples, by a semicolon, e.g. "a,a;b,b;c,c"
  - The fifth line contains the list of states of the automata, separated by commas, e.g. "qa,qb,qbb,qc,qf"
  - The sixth line has the initial state. It has to be one of the states listed above.
  - The seventh line has the list of final states, separated by commas. They have to be in the list of states.
  - From the eighth line onwards, each line contains a transition, written as "<origin state>;<symbols of upper strand separated by commas>;<symbols of lower strand separated by commas>;<destinarion state>". E.g. "qa;a;;qa".
    If the automata is probabilistic, the probability of a transition is specified in its line at the end separated from the transition by a vertical bar. E.g. "qa;a;;qa|0.4"
  
The repository contains some valid examples of WKFA specifications just in case something is unclear.
