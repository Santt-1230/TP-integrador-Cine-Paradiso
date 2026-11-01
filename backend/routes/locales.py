import logging
from flask import Blueprint, jsonify, request
import mysql.connector
import utils as ut
import constants as const
from services import salas as locales_services

logger = logging.getLogger(__name__)
locales_bp = Blueprint('locales', __name__, url_prefix='/api')
