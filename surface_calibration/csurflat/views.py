from django.shortcuts import render, redirect
from django.views import View

from .models import WorkOrder

import numpy as np
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import StringIO

# Create your views here.

class HomeView(View):

    def get(self, request, *args, **kwargs):

        list_work_orders = WorkOrder.objects.all()

        context = {
            "all_work_orders": list_work_orders,
        }

        return render(request, "home.html", context)
    
    def post(self, request, *args, **kwargs):

        work_order_id = request.POST.get('work_order_id').replace('/','%')

        return redirect("work_order_detail", wid=work_order_id)
    
class WorkOrderDetailView(View):

    def get(self, request, *args, **kwargs):
        
        work_order_id = self.kwargs['wid'].replace('%','/')
        work_order = WorkOrder.objects.get(work_order_number=work_order_id)

        context = {
            "work_order_number": work_order_id.replace('/','%'),
            "customer": work_order.customer,
            "ref": work_order.ref,
            "date_created": work_order.date_created,
            "surface_plate_id": work_order.surface_plate_id,
            "desc": work_order.description,
            "surface_plate_type": work_order.surface_plate_type,
            "length": work_order.length,
            "width": work_order.width,
            "grade": work_order.grade,
            "num_rows": work_order.num_rows,
            "num_cols": work_order.num_cols,
            "bridge_length": work_order.bridge_length,
            "start_temp": work_order.start_temp,
            "end_temp": work_order.end_temp,
        }

        return render(request, "work_order_detail.html", context)
    
    def post(self, request, *args, **kwargs):

        work_order_id = self.kwargs['wid']

        if('measurement_data_btn' in request.POST):
            return redirect("measurement_data", wid=work_order_id)
        
        if('flatness_btn' in request.POST):
            return redirect("flatness_data", wid=work_order_id)
        
        if('deviation_plot_btn' in request.POST):
            return redirect("deviation_plot", wid=work_order_id)
    
        # return render(request, "temp.html")
        
class MeasurementDataView(View):

    def get(self, request, *args, **kwargs):

        work_order_id = self.kwargs['wid'].replace('%','/')
        work_order = WorkOrder.objects.get(work_order_number=work_order_id)

        along_rows = [list(d.values()) for d in work_order.along_rows]
        across_rows = [list(d.values()) for d in work_order.across_rows]
        

        context = {
            "work_order_number": work_order_id.replace('/','%'),
            "num_rows": work_order.num_rows,
            "num_cols": work_order.num_cols,
            "rows": range(work_order.num_rows),
            "cols": range(work_order.num_cols),
            "along_rows": along_rows,
            "across_rows": across_rows,
        }

        return render(request, "measurement_data.html", context)
    
    def post(self, request, *args, **kwargs):

        work_order_id = self.kwargs['wid']

        if('work_order_btn' in request.POST):
            return redirect("work_order_detail", wid=work_order_id)
        
        if('flatness_btn' in request.POST):
            return redirect("flatness_data", wid=work_order_id)
        
        if('deviation_plot_btn' in request.POST):
            return redirect("deviation_plot", wid=work_order_id)

        return render(request, "temp.html")
    
class FlatnessView(View):


    def get(self, request, *args, **kwargs):

        work_order_id = self.kwargs['wid'].replace('%','/')
        work_order = WorkOrder.objects.get(work_order_number=work_order_id)

        if(work_order.flatness):
            flatness = work_order.flatness

        else:
            angular_deviation_along_rows = [list(d.values()) for d in work_order.along_rows]
            angular_deviation_across_rows = [list(d.values()) for d in work_order.across_rows]
            length = float(work_order.length)
            width = float(work_order.width)

            horizontal_step = length/(work_order.num_cols-1)
            vertical_step = width/(work_order.num_rows-1)

            linear_deviation_along_rows = np.array([[horizontal_step*i*np.tan(float(x)/3600) for i,x in enumerate(row)] for row in angular_deviation_along_rows])
            linear_deviation_across_rows = np.array([[vertical_step*i*np.tan(float(x)/3600) for x in row] for i,row in enumerate(angular_deviation_across_rows)])

            average_linear_deviation = (linear_deviation_along_rows.flatten() + linear_deviation_across_rows.flatten())/2
            X = np.array([[vertical_step*i for j in range(work_order.num_cols)] for i in range(work_order.num_rows)])
            Y = np.array([[horizontal_step*j for j in range(work_order.num_cols)] for i in range(work_order.num_rows)])

            X = X.flatten().reshape(-1,1)
            Y = Y.flatten().reshape(-1,1)  

            data_matrix = np.hstack([X, Y, np.ones_like(X)])

            # Fit a linear regression model
            model = LinearRegression()
            model.fit(data_matrix, average_linear_deviation)

            # Coefficients of the regression plane
            a, b, c = model.coef_ 

            distances = (a * X.flatten() + b * Y.flatten() - average_linear_deviation + c) / np.sqrt(a**2 + b**2 + 1)
            distances = distances.reshape((work_order.num_rows,work_order.num_cols))

            json_result = []

            for row_idx in range(distances.shape[0]):
                row_dict = {}
                for col_idx in range(distances.shape[1]):
                    col_name = f"COLUMN {col_idx + 1}"
                    row_dict[col_name] = f"{distances[row_idx, col_idx]*1000:.1f}"
                json_result.append(row_dict)

            flatness = json_result

            work_order.flatness = flatness
            work_order.save()

        flatness = np.array([list(d.values()) for d in flatness]).astype(float)

        context = {
            "work_order_number": work_order_id.replace('/','%'),
            "num_rows": work_order.num_rows,
            "num_cols": work_order.num_cols,
            "cols": range(work_order.num_cols),
            "flatness_data": flatness,
            "max_deviation": np.max(flatness),
            "min_deviation": np.min(flatness),
            "flatness": round(np.max(flatness)-np.min(flatness),1)
        }

        return render(request, "flatness_data.html", context)

    def post(self, request, *args, **kwargs):

        work_order_id = self.kwargs['wid']

        if('work_order_btn' in request.POST):
            return redirect("work_order_detail", wid=work_order_id)
        
        if('measurement_data_btn' in request.POST):
            return redirect("measurement_data", wid=work_order_id)
        
        if('deviation_plot_btn' in request.POST):
            return redirect("deviation_plot", wid=work_order_id)    

        return render(request, "temp.html")

class DeviationPlotView(View):

    def get(self, request, *args, **kwargs):
        
        work_order_id = self.kwargs['wid'].replace('%','/')
        work_order = WorkOrder.objects.get(work_order_number=work_order_id)

        flatness = np.array([list(d.values()) for d in work_order.flatness]).astype(float)

        x_data = np.arange(1,work_order.num_rows+1)
        y_data = np.arange(1,work_order.num_cols+1)
        X,Y = np.meshgrid(y_data,x_data)

        fig = plt.figure(figsize=(8,8))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_wireframe(Y, X, np.zeros((work_order.num_rows,work_order.num_cols)), linestyle='dotted', color='black', alpha=0.5)
        ax.plot_wireframe(Y, X, flatness/1000, color='blue')
        
        ax.set_xticks(x_data)
        ax.set_yticks(y_data)
        ax.set_zticks([-0.1,0,0.1])

        # Set labels
        ax.set_xlabel('Rows')
        ax.set_ylabel('Columns')
        ax.set_zlabel('Flatness Deviation (mm)')

        ax.view_init(20,-20)

        imgdata = StringIO()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)
        
        data = imgdata.getvalue()

        plt.close()

        # html_plot = mpld3.fig_to_html(fig)

        
        

        context = {
            "work_order_number": work_order_id.replace('/','%'),
            "html_plot": data,
        }

        return render(request, "deviation_plot.html", context)

    def post(self, request, *args, **kwargs):
        
        work_order_id = self.kwargs['wid']

        if('work_order_btn' in request.POST):
            return redirect("work_order_detail", wid=work_order_id)
        
        if('measurement_data_btn' in request.POST):
            return redirect("measurement_data", wid=work_order_id)
        
        if('flatness_btn' in request.POST):
            return redirect("flatness_data", wid=work_order_id)



