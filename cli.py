import click
from models import Product, Order
from fastapi_client import FastAPIClient

client = FastAPIClient(base_url='http://localhost:8000')

@click.group()
def cli():
    pass

@cli.command()
@click.argument('product_id', type=int)
def get_product(product_id):
    response = client.get(f'/products/{product_id}')
    if response.status_code == 200:
        product = response.json()
        click.echo(f"Product ID: {product['id']}\nName: {product['name']}\nPrice: {product['price']}")
    else:
        click.echo('Product not found', err=True)

@cli.command()
@click.argument('order', type=str)
def create_order(order):
    response = client.post('/orders', json=order)
    if response.status_code == 200:
        order = response.json()
        click.echo(f"Order ID: {order['id']}\nTotal: {order['total']}")
    else:
        click.echo('Failed to create order', err=True)


if __name__ == '__main__':
    cli()