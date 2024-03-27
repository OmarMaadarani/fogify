import os

from flask_sqlalchemy import SQLAlchemy

from connectors import get_connector
from utils.async_task import AsyncTask
from utils.host_info import HostInfo
from utils.logging import FogifyLogger
from utils.network import NetworkController
logger = FogifyLogger(__name__)


class Agent(object):
    """ The agent class that includes essential functionalities, namely,
   the agent's API, monitoring thread and docker's listener"""

    db = None

    def __init__(self, args, app):
        """
        It instantiates the agent and starts the API server
        :param args:
        :param app:
        """
        db_path = os.getcwd() + '/agent_database.db'

        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

        Agent.db = SQLAlchemy(app)
        if os.path.exists(db_path): os.remove(db_path)
        os.mknod(db_path)

        app.config['UPLOAD_FOLDER'] = "/current_agent/"
        os.environ['UPLOAD_FOLDER'] = "/current_agent/"
        if not os.path.exists(os.getcwd() + app.config['UPLOAD_FOLDER']):
            os.mkdir(os.getcwd() + app.config['UPLOAD_FOLDER'])

        connector = get_connector()
        app.config['CONNECTOR'] = connector
        app.config['NETWORK_CONTROLLER'] = NetworkController(connector)
        
        from utils.monitoring import PrometheusHandler, MetricCollector
        app.config['PROMETHEUS'] = PrometheusHandler(args.agent_ip, '9091', 'fogify')
        node_labels = {}

        if 'LABELS' in os.environ:
            node_labels = {i.split(":")[0]: i.split(":")[1] for i in os.environ['LABELS'].split(",") if
                           len(i.split(":")) == 2}

        node_labels.update(HostInfo.get_all_properties())  # TODO update this part to introduce custom compute devices
        connector.inject_labels(node_labels, HOST_IP=os.environ['HOST_IP'] if 'HOST_IP' in os.environ else None)

        #from utils.monitoring import MetricCollector
        from agent.views import MonitoringAPI, ActionsAPI, TopologyAPI, DistributionAPI, SnifferAPI, PrometheusAPI

        # Add the api routes
        app.add_url_rule('/topology/', view_func=TopologyAPI.as_view('Topology'))
        app.add_url_rule('/monitorings/', view_func=MonitoringAPI.as_view('Monitoring'))
        app.add_url_rule('/actions/', view_func=ActionsAPI.as_view('Action'))
        app.add_url_rule('/packets/', view_func=SnifferAPI.as_view('Packet'))
        app.add_url_rule('/generate-network-distribution/<string:name>/',
                         view_func=DistributionAPI.as_view('NetworkDistribution'))
        app.add_url_rule('/prom-metrics/', view_func=PrometheusAPI.as_view("PromMetrics"))
        logger.info("Agent routes are installed")
        # The thread that runs the monitoring agent
        metric_controller = MetricCollector()
        metric_controller_task = AsyncTask(metric_controller, 'start_monitoring', [args.agent_ip, connector, 5])
        metric_controller_task.start()
        logger.info("Monitoring process is started")

        # The thread that inspect containers and apply network QoS
        network_controller = NetworkController(connector)
        network_controller_task = AsyncTask(network_controller, 'listen', [])
        network_controller_task.start()
        logger.info("Agent network controller is started")


        self.app = app
        self.args = args
