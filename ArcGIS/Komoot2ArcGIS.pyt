import arcpy


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Komoot Toolbox"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [ImportRoute]


class ImportRoute(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Import Komoot Route"
        self.description = "Import komoot routes"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        routeID = arcpy.Parameter(
            displayName="Route ID",
            name="routeID",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        routeID.value="41193460"
        featureLayer= arcpy.Parameter(
            displayName = "Point Feature Layer",
            name="FeatureLayer",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Output")
        featureLayer.value="KomootRoutePoints"
        featureLayerLine= arcpy.Parameter(
            displayName = "Line Feature Layer",
            name="FeatureLayerLIne",
            datatype="GPFeatureLayer",
            parameterType="Optional",
            direction="Output")
        featureLayerLine.value="KomootRouteLine"
        params = [routeID, featureLayer, featureLayerLine]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        import urllib.request, json, os
        fc_name=os.path.basename(parameters[1].valueAsText)
        fc_line_name = os.path.basename(parameters[2].valueAsText)
        arcpy.AddMessage("We collect your data!")
        ###getting the route information###
        if not parameters[0].value:
            parameters[0].value = "41193460"
        with urllib.request.urlopen("https://api.komoot.de/v007/tours/" + parameters[0].value + "/coordinates") as url:
            data = json.loads(url.read())
        arcpy.AddMessage("Number of points: " + str(len(data["items"])))
        ###creating feature class for route storage###
        fc_fields = (  
            ("height", "SHORT", "", None, None, "", "NULLABLE", "NON_REQUIRED"),  
            ("time", "LONG", 8, None, None, "", "NULLABLE", "NON_REQUIRED") 
        )  
        arcpy.AddMessage("creating feature class " + fc_name)
        fc = arcpy.CreateFeatureclass_management(arcpy.env.workspace, fc_name, "POINT", spatial_reference=arcpy.SpatialReference(4326))  
        for fc_field in fc_fields:  
            arcpy.AddField_management(fc, *fc_field)  
        cursor = arcpy.da.InsertCursor(parameters[1].valueAsText,['height', 'time', 'SHAPE@XY'])
        
        for point in data["items"]:
            cursor.insertRow((point["alt"], point["t"], (point["lng"], point["lat"])))
        del cursor
        parameters[1].value = fc
        ###now create a second file for the polyline###
        parameters[2].value = arcpy.management.PointsToLine(parameters[1].valueAsText, parameters[2].valueAsText, None, None, "NO_CLOSE")
        return
