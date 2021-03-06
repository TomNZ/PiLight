import PropTypes from 'prop-types';
import React from 'react';
import {FormControl, FormGroup} from 'react-bootstrap';

import css from './common.scss';


const VALID_LONG = /^[-+]?[0-9]+?$/;

export class Long extends React.Component {
    static propTypes = {
        onChange: PropTypes.func.isRequired,
        value: PropTypes.number.isRequired,
        origValue: PropTypes.number.isRequired,
    };

    constructor(props) {
        super(props);
        this.state = {
            text: props.value.toString(),
            valid: true,
        }
    }

    componentWillReceiveProps(nextProps) {
        if (nextProps.value !== this.props.value) {
            // Reset the current value
            this.setState({
                text: nextProps.value.toString(),
                valid: true,
            });
        }
    }

    onChangeEvent = (event) => {
        const valueStr = event.target.value;
        let valid = VALID_LONG.test(valueStr);
        this.setState({
            text: valueStr,
            valid: valid,
        });

        if (!valid) {
            return;
        }

        this.props.onChange(parseInt(valueStr, 10));
    };

    render() {
        const edited = this.state.text !== this.props.origValue.toString();

        return (
            <FormGroup
                className={css.formGroup}
                validationState={edited ? (this.state.valid ? 'success' : 'error') : null}
            >
                <FormControl
                    bsSize="small"
                    className={css.controlWidth}
                    onChange={this.onChangeEvent}
                    type="number"
                    value={this.state.text}
                />
            </FormGroup>
        );
    }
}
