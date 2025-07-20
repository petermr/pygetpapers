<?xml version="1.0" encoding="UTF-8"?>
<p:declare-step xmlns:p="http://www.w3.org/ns/xproc"
  xmlns:c="http://www.w3.org/ns/xproc-step" 
  xmlns:tr="http://transpect.io"
  xmlns:jats="http://jats.nlm.nih.gov"
  version="1.0" 
  name="jats2html-driver"
  type="tr:jats2html">
  
  <p:documentation>
    This is the fallback pipeline when no other 
    pipeline could be found while evaluating the transpect
    cascade configuration. The pipeline invokes three
    XSLT modes to convert JATS or BITS to HTML.
  </p:documentation>
  
  <p:input port="source" primary="true"/>
  <p:input port="stylesheet" primary="false"/>
  <p:input port="parameters" kind="parameter" primary="true"/>
  
  <p:output port="result" primary="true"/>
  <p:output port="report" sequence="true">
    <p:pipe port="report" step="epub-alternatives"/>
    <p:pipe port="report" step="jats2html"/>
    <p:pipe port="report" step="clean-up"/>
  </p:output>
  
  <p:option name="debug" select="'no'"/>
  <p:option name="debug-dir-uri" select="'debug'"/>
  
  <p:import href="http://xmlcalabash.com/extension/steps/library-1.0.xpl"/>
  <p:import href="http://transpect.io/xproc-util/xslt-mode/xpl/xslt-mode.xpl"/>
  
  <tr:xslt-mode prefix="jats2html/01" mode="epub-alternatives" name="epub-alternatives">
    <p:input port="models">
      <p:empty/>
    </p:input>
    <p:input port="stylesheet">
      <p:pipe step="jats2html-driver" port="stylesheet"/>
    </p:input>
    <p:input port="parameters">
      <p:pipe port="parameters" step="jats2html-driver"/>
    </p:input>
    <p:with-option name="debug" select="$debug"/>
    <p:with-option name="debug-dir-uri" select="$debug-dir-uri"/>
  </tr:xslt-mode>
  
  <tr:xslt-mode prefix="jats2html/02" mode="jats2html" name="jats2html">
    <p:input port="models">
      <p:empty/>
    </p:input>
    <p:input port="stylesheet">
      <p:pipe step="jats2html-driver" port="stylesheet"/>
    </p:input>
    <p:input port="parameters">
      <p:pipe port="parameters" step="jats2html-driver"/>
    </p:input>
    <p:with-option name="debug" select="$debug"/>
    <p:with-option name="debug-dir-uri" select="$debug-dir-uri"/>
  </tr:xslt-mode>
  
  <tr:xslt-mode prefix="jats2html/03" mode="clean-up" name="clean-up">
    <p:input port="models">
      <p:empty/>
    </p:input>
    <p:input port="stylesheet">
      <p:pipe step="jats2html-driver" port="stylesheet"/>
    </p:input>
    <p:input port="parameters">
      <p:pipe port="parameters" step="jats2html-driver"/>
    </p:input>
    <p:with-option name="debug" select="$debug"/>
    <p:with-option name="debug-dir-uri" select="$debug-dir-uri"/>
  </tr:xslt-mode>
  
</p:declare-step>