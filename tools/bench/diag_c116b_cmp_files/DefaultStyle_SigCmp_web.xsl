<?xml version="1.0" encoding="UTF-8"?>
<!-- Edited by XMLSpy -->
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:o="urn:schemas-microsoft-com:office:office"
	xmlns:w="http://schemas.microsoft.com/office/word/5003/wordml" 
	xmlns:msxsl="urn:schemas-microsoft-com:xslt" 
	xmlns:v="urn:schemas-microsoft-com:vml">
<xsl:template match="/">
	<html>
		<head>
			<title>
				LabVIEW Compare Tool Report
			</title>
		</head>		
		<body topmargin="150" bottommargin="150">
			<div style="width:100%" align="center">
			<table border="0">
				<tr>
					<td colspan="16"><strong><font size="+4" face="Arial" color="#4F81BC">LabVIEW VI Comparison Report</font></strong></td>
				</tr>
				<tr>
					<td width="50"></td><td width="50"></td><td width="50"></td><td width="50"></td><td width="50"></td>
					<td width="50"></td><td width="50"></td><td width="50"></td><td width="50"></td><td width="50"></td>
					<td width="50"></td><td width="50"></td><td width="50"></td><td width="50"></td><td width="50"></td>
					<td width="50"></td>
				</tr>
				<tr>
					<td colspan="16"><strong><span style="line-height:20px;"><font size="-10" face="Arial" color="#FFFFFF">.</font></span></strong></td>
				</tr>
				<tr>
					<td colspan="16"><strong><font size="+2" face="Arial" color="#4F81BC">General Information</font></strong></td>
				</tr>	
				<tr>
					<td colspan="16"><HR color="#4F81BC" /></td>
				</tr>
				<tr>
					<td colspan="8"><strong><font face="">Report Generation Time</font></strong></td>
					<td colspan="8"><xsl:value-of select="report/basicInfo/@genTime" /></td>
				</tr>
				<xsl:if test="report/basicInfo/@description != ''">
					<tr>
						<td colspan="16"><strong><font face="">Description</font></strong></td>
					</tr>
					<tr>
						<td colspan="2" />
						<td colspan="13"><xsl:value-of select="report/basicInfo/@description" /></td>
						<td colspan="1" />
					</tr>
				</xsl:if>
				<tr>
					<td colspan="16"><strong><font face="">Compared Items</font></strong></td>
				</tr>
				<xsl:for-each select="report/detailInfo/comparedVIs/statistic/numChanges">
					<tr>
						<td colspan="1" />
						<td colspan="7"><xsl:value-of select="@type"/></td>
						<td colspan="8"/>
					</tr>
				</xsl:for-each>
				<tr>
					<td colspan="16"><strong><span style="line-height:20px;"><font size="-10" face="Arial" color="#FFFFFF">.</font></span></strong></td>
				</tr>
				<tr>
					<td colspan="16"><strong><font size="+2" face="Arial" color="#4F81BC">Detailed Information</font></strong></td>
				</tr>
				<tr>
					<td colspan="16"><HR color="#4F81BC"/></td>
				</tr>
				<xsl:for-each select="report/detailInfo/comparedVIs">
					<tr>
						<td colspan="16"><strong><font face="">First VI: <xsl:value-of select="@path1"/></font></strong>
							<xsl:if test="@notes1 != ''">
								(<xsl:value-of select="@notes1" />)
							</xsl:if>
						</td>
					</tr>
					<tr>
						<td colspan="16"><strong><font face="">Second VI: <xsl:value-of select="@path2" /></font></strong>
							<xsl:if test="@notes2 != ''">
								(<xsl:value-of select="@notes2" />)
							</xsl:if>
						</td>
					</tr>
					<tr>
						<td/>
						<td colspan="16"><li><strong><font face="">Result Statistics</font></strong></li></td>
					</tr>	
					<tr>
						<td colspan="2" />
						<td colspan="6"><u>Compared Items</u></td>
						<td	colspan="8"><u>Number of Changes</u></td>
					</tr>
					<xsl:for-each select="statistic/numChanges">
						<tr>
							<td colspan="2" />
							<td colspan="6"><xsl:value-of select="@type"/></td>
							<td colspan="8">
								<xsl:element name="a">
									<xsl:attribute name="href">
									<xsl:value-of select="@href"/>
									</xsl:attribute>
									<xsl:attribute name="target">_parent</xsl:attribute>
									<xsl:value-of select="@num"></xsl:value-of>
								</xsl:element>
							</td>
						</tr>
					</xsl:for-each>
				<xsl:if test="statistic/comparedItems/fpItems/@funcItem='T'">					
					<tr>
						<td />
						<td colspan="7"><li><strong><font face=""><a name="{fpChanges/@funcAnchor}">Front Panel Changes</a></font></strong></li></td>
						<xsl:if test="count(fpChanges/funcChanges)=0">
							<td colspan="9">None</td>
						</xsl:if>
					</tr>
					<xsl:for-each select="fpChanges/funcChanges">
						<tr>
							<td colspan="1"/>
							<td colspan="1"><xsl:number value = "position()" format = "1)"/></td>
							<td colspan="6">Difference Type</td>		
							<td colspan="8"><xsl:value-of select="@diffType" /></td>
						</tr>
						<xsl:if test="@objLabel != ''">
							<tr>	
								<td colspan="2"></td>							
								<td colspan="6">Object Label</td>		
								<td colspan="8"><xsl:value-of select="@objLabel" /></td>							
							</tr>
						</xsl:if>
						<xsl:if test="@objType != ''">						
							<tr>
								<td colspan="2"></td>
								<td colspan="6">Object Type</td>
								<td colspan="8"><xsl:value-of select="@objType" /></td>			
							</tr> 						
						</xsl:if>						
						<xsl:if test="@detailDesc != ''">
							<tr valign="top">
								<td colspan="2"></td>
								<td colspan="6">Detailed Description</td>		
								<td colspan="8" width="500"><xsl:value-of select="@detailDesc" /></td>
							</tr>
						</xsl:if>
						<xsl:if test="@imagePath1!=''">						
							<tr>					
								<td colspan="8" align="center" style="border-left:#000000 solid 1px; border-right:#000000 solid 1px; border-top:#000000 solid 1px; border-bottom:#000000 solid 1px;">
									<img width="500" src="{@imagePath1}" />
								</td>
								<td colspan="8" align="center" style="border-left:#000000 solid 1px; border-right:#000000 solid 1px; border-top:#000000 solid 1px; border-bottom:#000000 solid 1px;">
									<img width="500" src="{@imagePath2}" />
								</td>	
							</tr>
						</xsl:if>
					</xsl:for-each>
				</xsl:if>	
				<xsl:if test="statistic/comparedItems/fpItems/@cosmItem='T'">
					<tr>
						<td/>
						<td colspan="7"><li><strong><font face=""><a name="{fpChanges/@cosmAnchor}">Front Panel Position/Size Changes</a></font></strong></li></td>
						<xsl:if test="count(fpChanges/cosmChanges)=0">
							<td colspan="9">None</td>
						</xsl:if>
					</tr>
					<xsl:for-each select="fpChanges/cosmChanges">
						<tr>
							<td colspan="1"/>
							<td colspan="1"><xsl:number value = "position()" format = "1)"/></td>	
							<td colspan="6">Difference Type</td>	
							<td colspan="8"><xsl:value-of select="@diffType" /></td>
						</tr>
						<xsl:if test="@objLabel != ''">
							<tr>	
								<td colspan="2"></td>							
								<td colspan="6">Object Label</td>		
								<td colspan="8"><xsl:value-of select="@objLabel" /></td>							
							</tr>
						</xsl:if>
						<xsl:if test="@objType != ''">						
							<tr>
								<td colspan="2"></td>
								<td colspan="6">Object Type</td>
								<td colspan="8"><xsl:value-of select="@objType" /></td>			
							</tr> 						
						</xsl:if>						
						<xsl:if test="@detailDesc != ''">
							<tr valign="top">
								<td colspan="2"></td>
								<td colspan="6">Detailed Description</td>		
								<td colspan="8" width="500"><xsl:value-of select="@detailDesc" /></td>
							</tr>
						</xsl:if>
						<xsl:if test="@imagePath1!=''">						
							<tr>					
								<td colspan="8" align="center" style="border-left:#000000 solid 1px; border-right:#000000 solid 1px; border-top:#000000 solid 1px; border-bottom:#000000 solid 1px;">
									<img width="500" src="{@imagePath1}" />
								</td>
								<td colspan="8" align="center" style="border-left:#000000 solid 1px; border-right:#000000 solid 1px; border-top:#000000 solid 1px; border-bottom:#000000 solid 1px;">
									<img width="500" src="{@imagePath2}" />
								</td>	
							</tr>
						</xsl:if>
					</xsl:for-each>
				</xsl:if>
				<xsl:if test="statistic/comparedItems/bdItems/@funcItem='T'">
					<tr>
						<td />
						<td colspan="7"><li><strong><font face=""><a name="{bdChanges/@funcAnchor}">Block Diagram Functional Changes</a></font></strong></li></td>
						<xsl:if test="count(bdChanges/funcChanges)=0">
							<td colspan="9">None</td>
						</xsl:if>
					</tr>
					<xsl:for-each select="bdChanges/funcChanges">
						<tr>
							<td colspan="1"/>
							<td colspan="1"><xsl:number value = "position()" format = "1)"/></td>
							<td colspan="6">Difference Type</td>		
							<td colspan="8"><xsl:value-of select="@diffType" /></td>
						</tr>
						<xsl:if test="@objLabel != ''">
							<tr>	
								<td colspan="2"></td>							
								<td colspan="6">Object Label</td>		
								<td colspan="8"><xsl:value-of select="@objLabel" /></td>							
							</tr>
						</xsl:if>
						<xsl:if test="@objType != ''">						
							<tr>
								<td colspan="2"></td>
								<td colspan="6">Object Type</td>
								<td colspan="8"><xsl:value-of select="@objType" /></td>			
							</tr> 						</xsl:if>
						
						<xsl:if test="@detailDesc != ''">
							<tr valign="top">
								<td colspan="2"></td>
								<td colspan="6">Detailed Description</td>		
								<td colspan="8" width="500"><xsl:value-of select="@detailDesc" /></td>
							</tr>
						</xsl:if>
						<xsl:if test="@imagePath1!=''">						
							<tr>					
								<td colspan="8" align="center" style="border-left:#000000 solid 1px; border-right:#000000 solid 1px; border-top:#000000 solid 1px; border-bottom:#000000 solid 1px;">
									<img width="500" src="{@imagePath1}" />
								</td>
								<td colspan="8" align="center" style="border-left:#000000 solid 1px; border-right:#000000 solid 1px; border-top:#000000 solid 1px; border-bottom:#000000 solid 1px;">
									<img width="500" src="{@imagePath2}" />
								</td>	
							</tr>
						</xsl:if>
					</xsl:for-each>
				</xsl:if>
				<xsl:if test="statistic/comparedItems/bdItems/@cosmItem='T'">
					<tr>
						<td />
						<td colspan="7"><li><strong><font face=""><a name="{bdChanges/@cosmAnchor}">Block Diagram Cosmetic Changes</a></font></strong></li></td>
						<xsl:if test="count(bdChanges/cosmChanges)=0">
							<td colspan="9">None</td>
						</xsl:if>
					</tr>
					<xsl:for-each select="bdChanges/cosmChanges">
						<tr>
							<td colspan="1"/>
							<td colspan="1"><xsl:number value = "position()" format = "1)"/></td>
							<td colspan="6">Difference Type</td>		
							<td colspan="8"><xsl:value-of select="@diffType" /></td>
						</tr>
						<xsl:if test="@objLabel != ''">
							<tr>	
								<td colspan="2"></td>							
								<td colspan="6">Object Label</td>		
								<td colspan="8"><xsl:value-of select="@objLabel" /></td>							
							</tr>
						</xsl:if>
						<xsl:if test="@objType != ''">						
							<tr>
								<td colspan="2"></td>
								<td colspan="6">Object Type</td>
								<td colspan="8"><xsl:value-of select="@objType" /></td>			
							</tr> 						</xsl:if>
						
						<xsl:if test="@detailDesc != ''">
							<tr valign="top">
								<td colspan="2"></td>
								<td colspan="6">Detailed Description</td>		
								<td colspan="8" width="500"><xsl:value-of select="@detailDesc" /></td>
							</tr>
						</xsl:if>
						<xsl:if test="@imagePath1!=''">						
							<tr>					
								<td colspan="8" align="center" style="border-left:#000000 solid 1px; border-right:#000000 solid 1px; border-top:#000000 solid 1px; border-bottom:#000000 solid 1px;">
									<img width="500" src="{@imagePath1}" />
								</td>
								<td colspan="8" align="center" style="border-left:#000000 solid 1px; border-right:#000000 solid 1px; border-top:#000000 solid 1px; border-bottom:#000000 solid 1px;">
									<img width="500" src="{@imagePath2}" />
								</td>	
							</tr>
						</xsl:if>
					</xsl:for-each>
				</xsl:if>
				<xsl:if test="statistic/comparedItems/atrItems/@atrItem='T'">
					<tr>
						<td />
						<td colspan="7"><li><strong><font face=""><a name="{attrChanges/@atrAnchor}">VI Attributes Changes</a></font></strong></li></td>
						<xsl:if test="count(attrChanges/attrChange)=0">
							<td colspan="9">None</td>
						</xsl:if>
					</tr>
					<xsl:for-each select="attrChanges/attrChange">
						<tr>
							<td colspan="1"/>
							<td colspan="1"><xsl:number value = "position()" format = "1)"/></td>
							<td colspan="6">Difference Type</td>		
							<td colspan="8"><xsl:value-of select="@diffType" /></td>
						</tr>
						<xsl:if test="@attrType != ''">
							<tr>	
								<td colspan="2"></td>							
								<td colspan="6">Attribute Type</td>		
								<td colspan="8"><xsl:value-of select="@attrType" /></td>							
							</tr>
						</xsl:if>
						<xsl:if test="@detailDesc != ''">
							<tr valign="top">
								<td colspan="2"></td>
								<td colspan="6">Detailed Description</td>		
								<td colspan="8" width="500"><xsl:value-of select="@detailDesc" /></td>
							</tr>
						</xsl:if>
					</xsl:for-each>
				</xsl:if>
				<tr>
					<td colspan="16"><HR style="border:1 dashed " color="#4F81BC"/></td>
				</tr>
				</xsl:for-each>
				<tr>
					<td colspan="16"><HR color="#4F81BC"/></td>
				</tr>
				<!--<tr>
					<td colspan="16" align="right"><font size="-1" color="#4F81BC">© 2013 National Instruments. All rights reserved.</font></td>
				</tr>-->
			</table>
			</div>
		</body>
	</html>
</xsl:template>
</xsl:stylesheet>


