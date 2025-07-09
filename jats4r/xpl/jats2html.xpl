<?xml version="1.0" encoding="utf-8"?>
<p:declare-step xmlns:p="http://www.w3.org/ns/xproc" 
  xmlns:c="http://www.w3.org/ns/xproc-step"    
  xmlns:tr="http://transpect.io"
  xmlns:jats="http://jats.nlm.nih.gov"
  version="1.0"
  name="jats-jats2html"
  type="jats:html">
  
  <p:documentation>
    This step converts JATS or BITS to HTML. The step
    expects a transpect paths document as secondary input
    to dynamically load a matching XProc driver.
  </p:documentation>
  
  <p:option name="srcpaths" required="false" select="'no'"/>
  <p:option name="debug" required="false" select="'no'"/>
  <p:option name="debug-dir-uri" required="false" select="'debug'"/>
  <p:option name="status-dir-uri" required="false" select="'status'"/>
  <p:option name="css-location" required="false" select="''"/>
  <p:option name="fallback-xsl" select="'http://transpect.io/jats2html/xsl/jats2html.xsl'"/>
  <p:option name="fallback-xpl" select="'http://transpect.io/jats2html/xpl/jats2html_default.xpl'"/>
  
  <p:input port="source" primary="true"/>
  <p:input port="paths" kind="parameter" primary="true"/>
  <p:output port="result" primary="true" />
  <p:output port="report" sequence="true">
    <p:pipe port="report" step="dtp"/>
  </p:output>
  
  <p:import href="http://transpect.io/cascade/xpl/dynamic-transformation-pipeline.xpl"/>
  <p:import href="http://transpect.io/xproc-util/xml-model/xpl/prepend-xml-model.xpl" />
  <p:import href="http://transpect.io/xproc-util/simple-progress-msg/xpl/simple-progress-msg.xpl"/>
  
  <tr:simple-progress-msg name="start-msg" file="jats2html-start.txt">
    <p:input port="msgs">
      <p:inline>
        <c:messages>
          <c:message xml:lang="en">Starting JATS/BITS/HoBoTS to HTML conversion</c:message>
          <c:message xml:lang="de">Beginne Konvertierung von JATS/BITS/HoBoTS nach HTML</c:message>
        </c:messages>
      </p:inline>
    </p:input>
    <p:with-option name="status-dir-uri" select="$status-dir-uri"/>
  </tr:simple-progress-msg>
  
  <tr:dynamic-transformation-pipeline load="jats2html/jats2html" name="dtp">
    <p:with-option name="fallback-xsl" select="$fallback-xsl"/>
    <p:with-option name="fallback-xpl" select="$fallback-xpl"/>
    <p:with-param name="css-location" select="$css-location"/>
    <p:with-param name="srcpaths" select="$srcpaths"/>
    <p:with-option name="debug" select="$debug"/>
    <p:with-option name="debug-dir-uri" select="$debug-dir-uri"/>
    <p:input port="source">
      <p:pipe port="source" step="jats-jats2html"/>
    </p:input>
    <p:input port="additional-inputs">
      <p:empty/>
    </p:input>
    <p:input port="options"><p:empty/></p:input>
    <p:pipeinfo>
      <examples xmlns="http://transpect.io"> 
        <collection dir-uri="http://this.transpect.io/a9s/" file="jats2html/xpl/jats2html.xpl"/>
        <generator-collection dir-uri="http://this.transpect.io/a9s/" file="jats2html/xpl/jats2html.xpl.xsl"/>
      </examples>
    </p:pipeinfo>
  </tr:dynamic-transformation-pipeline>

  <tr:simple-progress-msg name="success-msg" file="jats2html-success.txt">
    <p:input port="msgs">
      <p:inline>
        <c:messages>
          <c:message xml:lang="en">JATS/BITS/HoBoTS to HTML conversion successfully finished</c:message>
          <c:message xml:lang="de">Konvertierung von JATS/BITS/HoBoTS nach HTML erfolgreich abgeschlossen</c:message>
        </c:messages>
      </p:inline>
    </p:input>
    <p:with-option name="status-dir-uri" select="$status-dir-uri"/>
  </tr:simple-progress-msg>
  
</p:declare-step>
